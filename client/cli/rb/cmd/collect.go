package cmd

import (
	"context"
	"encoding/json"
	"io"
	"io/ioutil"
	"net/http"
	"net/url"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/sirupsen/logrus"
	"github.com/twinj/uuid"

	"github.com/roundbroker/roundbroker/client/rb"
	"github.com/roundbroker/roundbroker/client/sse"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

// collectCmd represents the collect command
var collectCmd = &cobra.Command{
	Use:   "collect",
	Short: "collect is the command that allows to retrieve API Calls from roundbroker.io and forward them to the underlying service",
	Long:  ``,
	Run: func(cmd *cobra.Command, args []string) {
		logrus.Infof("Starting SSE client to server %q. Redirecting requests to %q", viper.GetString("server.address"), viper.GetString("destination.service.url"))
		ctx, cancel := context.WithCancel(context.Background())
		defer cancel()
		go exposeMetrics(viper.GetString("metrics.address"), "/metrics")

		// create workers channel. This chan is used to announce that a worker can accept jobs
		workers := make(chan chan rb.Job, viper.GetInt("workers"))
		stchan := make(chan rb.Job)

		// start workers. Number of parallel workers is set by WORKER env variable
		for i := 0; i < viper.GetInt("workers"); i++ {
			go rb.Worker{StoreIDs: stchan}.Start(workers)
		}
		go rb.StoreRequestID(ctx, stchan)

		// create jobs channel to pass jobs around
		jobs := make(chan rb.Job, 1000)

		// Dispatch is the function that collect jobs and assign workers to do the task
		go rb.Dispatch(jobs, workers)

		// create events channel (sse client)
		re := make(chan *sse.Event, 1000)
		createSSERequest()
		go func() {
			err := sse.Notify(viper.GetString("server.address"), re)
			if err != nil {
				logrus.WithError(err).Errorf("An error happened with the SSE request")
			}
		}()

		baseURL, err := url.Parse(viper.GetString("destination.service.url"))
		if err != nil {
			logrus.Fatalf("Failed to parse destination service URL as valid URL: %v", viper.GetString("destination.service.url"))
		}

		// main loop. This loop retrieve requests from sse server and pass them to the
		// jobs chan.
		for {
			select {
			case content := <-re:
				// create receiving struct to parse events in response
				c := struct {
					PublishedAt string `json:"published_at"`
					PublishedOn string `json:"published_on"`
					ReceivedAt  string `json:"received_at"`
					Request     struct {
						ExtraPath string            `json:"extra_path"`
						Body      string            `json:"body"`
						Headers   map[string]string `json:"headers"`
						Args      string
						Method    string `json:"method"`
					} `json:""`
					SourceIP  string `json:"source_ip"`
					SourceURL string `json:"source_url"`
				}{}

				data, err := ioutil.ReadAll(content.Data)
				if err != nil {
					logrus.Errorf("Failed to read data from input message: %v", err)
					continue
				}
				logrus.Debugf("[RAW CONTENT]: %v", string(data))

				err = json.Unmarshal(data, &c)
				if err != nil {
					logrus.Errorf("Failed to decode body content as json response: %v", err)
					continue
				}
				logrus.Debugf("[PARSED STRUCT]: %v", c)

				// parse extrapath and add query arguments
				extraPath, err := url.Parse(c.Request.ExtraPath)
				if err != nil {
					logrus.Errorf(`Failed to decode "extra_path" as valid path. %q`, c.Request.ExtraPath)
					continue
				}
				extraPath.RawQuery = c.Request.Args

				// rebuild headers to the internal format. (in case the future struct from python is valid)
				headers := make(map[string][]string)
				for k, v := range c.Request.Headers {
					headers[k] = []string{v}
				}

				j := rb.Job{
					ID: content.ID,
					Request: rb.Request{
						ID:      uuid.NewV4().String(),
						Method:  c.Request.Method,
						Headers: headers,
						Body:    c.Request.Body,
						URI:     baseURL.ResolveReference(extraPath).String(),
					},
					StartDate: time.Now(),
				}
				logrus.Debugf("[JOB]: %v", j)
				jobs <- j

				rb.JobGauge.Inc()
				rb.RequestCount.Inc()
			}

			// ---------------------------------------------
			// Test code
			// ---------------------------------------------
			// headers := make(map[string][]string)
			// jobs <- rb.Job{
			// 	ID: uuid.NewV4().String(),
			// 	Request: rb.Request{
			// 		ID:      "test",
			// 		Method:  "GET",
			// 		Headers: headers,
			// 		Body:    []byte(``),
			// 		URI:     "http://localhost:10101/api/v1/play/insulte?tag",
			// 	},
			// 	StartDate: time.Now(),
			// }
			// rb.JobGauge.Inc()
			// rb.RequestCount.Inc()
			// time.Sleep(10 * time.Millisecond)
			// ---------------------------------------------
			// End of Test code
			// ---------------------------------------------
		}
	},
}

func init() {
	rootCmd.AddCommand(collectCmd)
	// collectCmd.Flags().StringP("url", "u", "http://roundbroker.io/c", "Url used to collect the API's request to replay")
	collectCmd.Flags().StringP("server", "s", "", "This set the pivot URL where you need to retrieve query to replay locally")
	viper.BindPFlag("server.address", collectCmd.Flags().Lookup("server"))

	collectCmd.Flags().StringP("destination", "d", "", "URL to send the received request to (http://internalapi:8081/v1/secretKey/")
	viper.BindPFlag("destination.service.url", collectCmd.Flags().Lookup("destination"))

	collectCmd.Flags().StringP("offset", "o", "", "Offset at which you want to start collect from")
	viper.BindPFlag("collect.offset", collectCmd.Flags().Lookup("offset"))

	collectCmd.Flags().BoolP("insecure", "k", false, "By default every request is made in a secure way to your internal applications. If you have self-signed certificate. no support for custom CA is currently done. You'd have to build your own docker image.")
	viper.BindPFlag("tls.insecure", collectCmd.Flags().Lookup("insecure"))

	prometheus.MustRegister(
		rb.WorkerGauge,
		rb.RequestCount,
		rb.JobGauge,
		rb.APIRequestDuration,
	)
}

func createSSERequest() {
	lastReqID := viper.GetString("collect.offset")
	var err error
	if lastReqID == "" {
		lastReqID, err = rb.LoadRequestID()
		if err != nil {
			logrus.WithField("err", err).Infof("Failed to read the store file of the consumed eventsID. If it doesn't exist, it will be created at with the first event received.")
		}
	}

	cuuid := viper.GetString("consumer.uuid")
	sse.GetReq = func(verb, uri string, body io.Reader) (*http.Request, error) {
		req, err := http.NewRequest(verb, uri, body)
		if err != nil {
			return nil, err
		}
		if lastReqID != "" {
			req.Header.Add("Last-Event-Id", lastReqID)
		}
		if cuuid != "" {
			req.Header.Add("X-Consumer-Uuid", cuuid)
		}

		return req, nil
	}
}

func exposeMetrics(addr string, path string) {
	http.Handle(path, promhttp.Handler())
	logrus.Fatal(http.ListenAndServe(addr, nil))
}
