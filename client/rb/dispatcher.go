package rb

import (
	"github.com/Sirupsen/logrus"
)

// Dispatch send job request to workers
func Dispatch(jobs chan Job, workers chan chan Job) {
	for {
		select {
		case job := <-jobs:
			logrus.Debug("Received a job to dispatch")
			worker := <-workers
			logrus.Debug("Found an available worker")
			worker <- job
			WorkerGauge.Dec()
			JobGauge.Dec()
		}
	}
}
