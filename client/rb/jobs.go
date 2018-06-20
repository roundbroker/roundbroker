package rb

import "time"

// Job is the struct that contains our work
type Job struct {
	// ID is the ID of the work
	ID string
	// Req is the request to forward to the end service
	Request Request
	// StartDate is the time at which the request is sent
	StartDate time.Time
	// EndDate is the time at which the response is received
	EndDate time.Time
}

// Request is the structure representing informations needed to make a request to the proxied
// service
type Request struct {
	// Id of the request
	ID string
	// Method used to call the requested service
	Method string
	// Headers used in the request
	Headers map[string][]string
	// Body is the content of the request
	Body string
	// URI is the path used for the request
	URI string
}
