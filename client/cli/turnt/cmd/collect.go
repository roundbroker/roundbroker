package cmd

import (
	"encoding/json"
	"io"
	"io/ioutil"
	"net/http"
	"time"

	"github.com/Sirupsen/logrus"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/prometheus/log"
	"github.com/twinj/uuid"

	"github.com/gbossert/APITurntable/client/sse"
	"github.com/gbossert/APITurntable/client/turnt"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

// collectCmd represents the collect command
var collectCmd = &cobra.Command{
	Use:   "collect",
	Short: "collect is the command that allows to retrieve API Calls from apiturntables.io and forward them to the underlying service",
	Long:  ``,
	Run: func(cmd *cobra.Command, args []string) {
		logrus.Infof("Starting SSE client to server %v", viper.GetString("server.address"))
		go exposeMetrics(":8080", "/metrics")

		// create workers channel. This chan is used to announce that a worker can accept jobs
		workers := make(chan chan turnt.Job, viper.GetInt("workers"))

		// start workers. Number of parallel workers is set by WORKER env variable
		for i := 0; i < viper.GetInt("workers"); i++ {
			go turnt.Worker{}.Start(workers)
		}

		// create jobs channel to pass jobs around
		jobs := make(chan turnt.Job, 1000)

		// Dispatch is the function that collect jobs and assign workers to do the task
		go turnt.Dispatch(jobs, workers)

		// create events channel (sse client)
		re := make(chan *sse.Event, 1000)
		createSSERequest()
		go sse.Notify(viper.GetString("server.address"), re)

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
						Body      []byte            `json:"body"`
						Headers   map[string]string `json:"headers"`
						Args      string
					} `json:""`
					Method    string `json:"method"`
					SourceIP  string `json:"source_ip"`
					SourceURL string `json:"source_url"`
				}{}

				data, err := ioutil.ReadAll(content.Data)
				if err != nil {
					log.Errorf("Failed to read data from input message: %v", err)
					continue
				}
				logrus.Debugf("[RAW CONTENT]: %v", string(data))

				err = json.Unmarshal(data, &c)
				if err != nil {
					log.Errorf("Failed to decode body content as json response: %v", err)
					continue
				}
				logrus.Debugf("[PARSED STRUCT]: %v", c)

				// rebuild headers to the internal format. (in case the future struct from python is valid)
				headers := make(map[string][]string)
				for k, v := range c.Request.Headers {
					headers[k] = []string{v}
				}

				j := turnt.Job{
					ID: content.ID,
					Request: turnt.Request{
						ID:      uuid.NewV4().String(),
						Method:  c.Method,
						Headers: headers,
						Body:    c.Request.Body,
						URI:     viper.GetString("destination.service.url") + "/" + c.Request.ExtraPath,
					},
					StartDate: time.Now(),
				}
				logrus.Debugf("[JOB]: %v", j)
				jobs <- j

				turnt.JobGauge.Inc()
				turnt.RequestCount.Inc()
			}

			// ---------------------------------------------
			// Test code
			// ---------------------------------------------
			// headers := make(map[string][]string)
			// jobs <- turnt.Job{
			// 	ID: uuid.NewV4().String(),
			// 	Request: turnt.Request{
			// 		ID:      "test",
			// 		Method:  "GET",
			// 		Headers: headers,
			// 		Body:    []byte(``),
			// 		URI:     "http://localhost:10101/api/v1/play/insulte?tag",
			// 	},
			// 	StartDate: time.Now(),
			// }
			// turnt.JobGauge.Inc()
			// turnt.RequestCount.Inc()
			// time.Sleep(10 * time.Millisecond)
			// ---------------------------------------------
			// End of Test code
			// ---------------------------------------------
		}
	},
}

func init() {
	rootCmd.AddCommand(collectCmd)
	// collectCmd.Flags().StringP("url", "u", "http://turntable.io/", "Url used to collect the API's request to replay")
	// collectCmd.Flags().StringP("target-type", "t", "final", `Type of destination. It can be "final" for proxying request or another supported type (ex: rabbitmq, redis, another apiturntable server, etc.)`)

	prometheus.MustRegister(
		turnt.WorkerGauge,
		turnt.RequestCount,
		turnt.JobGauge,
		turnt.APIRequestDuration,
	)
}

func createSSERequest() {
	// lastReqID := l.Load()
	lastReqID := ""
	sse.GetReq = func(verb, uri string, body io.Reader) (*http.Request, error) {
		req, err := http.NewRequest(verb, uri, body)
		if err != nil {
			return nil, err
		}
		if lastReqID != "" {
			req.Header.Add("Last-Event-Id", lastReqID)
		}
		return req, nil
	}
}

func exposeMetrics(addr string, path string) {
	http.Handle(path, promhttp.Handler())
	log.Fatal(http.ListenAndServe(addr, nil))
}
