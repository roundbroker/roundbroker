package turnt

import "context"

// StoreRequestID is used to store the state of the requests
// you have to launch this function in the main part of your application
// with a shared channel between the workers
// state of handled requests will be stored into a unique file.
// The lock is the main reason for the fan-in pattern
func StoreRequestID(ctx context.Context, requests chan Job) {
	for {
		select {
		case <-ctx.Done():
			break
		case req := <-requests:
			store(req)
		}
	}

}

func store(request Job) {
	// find request path
	// compute filepath to store the current eventID
	// save that id to that file
}
