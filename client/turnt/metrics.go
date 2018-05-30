package turnt

import "github.com/prometheus/client_golang/prometheus"

var (
	// PivotRequest = prometheus.NewHistogramVec()

	// RequestCount is the total count of request from the start of the application.
	RequestCount = prometheus.NewCounter(
		prometheus.CounterOpts{
			Name: "turnt_received_request_count",
			Help: "Count the number of job request received",
		},
	)

	// APIRequestDuration is the metric used to handle request durations. It has the label
	// "Method"
	APIRequestDuration = prometheus.NewHistogramVec(
		prometheus.HistogramOpts{
			Name: "turnt_api_request_sent_duration_seconds",
			Help: "Duration of the requests forwarded to the destination",
		},
		[]string{"Method"},
	)

	// WorkerNum = prometheus.NewCounter()

	// JobGauge is the queue counter. It counts job waiting to be dispatched to workers.
	JobGauge = prometheus.NewGauge(
		prometheus.GaugeOpts{
			Name: "turnt_waiting_jobs_count",
			Help: "Number jobs waiting to be handled",
		},
	)
	// WorkerGauge is the gauge to count worker waiting for jobs to be dispatched to them.
	WorkerGauge = prometheus.NewGauge(
		prometheus.GaugeOpts{
			Name: "turnt_workers_available_count",
			Help: "Number of workers available to handle jobs",
		},
	)
)
