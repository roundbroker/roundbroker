package rb

import (
	"io/ioutil"
	"net/http"
	"strings"
	"time"

	"github.com/Sirupsen/logrus"
	"github.com/twinj/uuid"
)

// Worker is the interface that is used to implement what to do with at job.
// An example Work function can be found below:
//  func Work(workers chan chan Job) {
//    workChan := make(chan Job)
//    go func() {
//      for {
//        // register the workChan to worker pool
//        workers <- workChan
//        select {
//        case job := <-workChan:
//          // handle the job
//        }
//      }
//    }()
//  }

type Worker struct {
	StoreIDs chan Job
}

// Start is the function to start a worker job
func (w Worker) Start(workers chan chan Job) {
	workChan := make(chan Job)
	wid := uuid.NewV4().String()
	go func() {
		for {
			workers <- workChan
			WorkerGauge.Inc()
			select {
			case job := <-workChan:
				// declare common fields for logger (error or debug)
				f := logrus.Fields{
					"workerID":    wid,
					"requestID":   job.ID,
					"startDate":   job.StartDate,
					"timeInQueue": time.Since(job.StartDate),
					"request":     job.Request,
				}

				// build request based on received job
				req, err := http.NewRequest(job.Request.Method, job.Request.URI, strings.NewReader(job.Request.Body))
				if err != nil {
					f["error"] = err
					logrus.WithFields(f).Errorf("Failed to build request from job")
					continue
				}
				// add headers to the request
				for k, v := range job.Request.Headers {
					for _, val := range v {
						req.Header.Add(k, val)
					}
				}
				// send requests
				reqStart := time.Now()
				resp, err := http.DefaultClient.Do(req)
				if err != nil {
					f["error"] = err
					logrus.WithFields(f).Errorf("Failed to forward the request to the server")
					continue
				}
				APIRequestDuration.WithLabelValues(job.Request.Method).Observe(time.Since(reqStart).Seconds())
				rc, err := ioutil.ReadAll(resp.Body)
				if err != nil {
					f["error"] = err
					logrus.WithFields(f).Errorf("Failed to read body content of the response")
					resp.Body.Close()
					continue
				}
				resp.Body.Close()
				f["request"] = req
				f["response"] = string(rc)
				f["responseStatusCode"] = resp.StatusCode
				logrus.WithFields(f).Info("Request sent to server")

				// save the fact that this event has been handled
				w.StoreIDs <- job

			}
		}
	}()
}
