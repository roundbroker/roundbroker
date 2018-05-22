package cmd

import (
	"encoding/json"
	"time"

	"github.com/Sirupsen/logrus"
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

		// create workers channel. This chan is used to announce that a worker can accept jobs
		workers := make(chan chan turnt.Job, viper.GetInt("workers"))

		// start workers. Number of parallel workers is set by WORKER env variable
		for i := 0; i < viper.GetInt("workers"); i++ {
			go turnt.Worker{}.Start(workers)
		}

		// create jobs channel to pass jobs around
		jobs := make(chan turnt.Job, 100)

		// Dispatch is the function that collect jobs and assign workers to do the task
		go turnt.Dispatch(jobs, workers)

		// create events channel (sse client)
		re := make(chan *sse.Event, 100)
		go sse.Notify(viper.GetString("server.address"), re)

		// main loop. This loop retrieve requests from sse server and pass them to the
		// jobs chan.
		for {
			select {
			case content := <-re:
				// create receiving struct to parse events in response
				c := struct {
					Items []struct {
						ID      string
						Request struct {
							URIAppend string
							Method    string
							Headers   map[string][]string
							Body      []byte
						}
					}
					Total int
				}{}

				err := json.NewDecoder(content.Data).Decode(c)
				if err != nil {
					log.Errorf("Failed to decode body content as json response: %v", err)
					continue
				}

				for _, job := range c.Items {
					jobs <- turnt.Job{
						ID: uuid.NewV4().String(),
						Request: turnt.Request{
							ID:      job.ID,
							Method:  job.Request.Method,
							Headers: job.Request.Headers,
							Body:    job.Request.Body,
							URI:     viper.GetString("destination.service.url") + job.Request.URIAppend,
						},
						StartDate: time.Now(),
					}
				}
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
			// time.Sleep(1 * time.Millisecond)
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
}
