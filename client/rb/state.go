package rb

import (
	"context"
	"fmt"
	"os"
	"path"

	"github.com/Sirupsen/logrus"
	"github.com/spf13/viper"
)

var storePath = "/var/tmp/"

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
			err := save(req, viper.GetString("serviceName"), viper.GetString("consumer.uuid"))
			if err != nil {
				logrus.WithField("err", err).Errorf("Failed to store the requestID in the state file.")
			}
		}
	}

}

// LoadRequestID return the current state of the
func LoadRequestID() (string, error) {
	return load(viper.GetString("serviceName"), viper.GetString("consumer.uuid"))
}

// SaveState will save the current state of the consumption in a file at the path
// /var/tmp/${SERVICE_NAME}/${CONSUMER_UUID}
func save(request Job, serviceName, cuuid string) error {
	spath := path.Join(storePath, serviceName, cuuid)

	if _, err := os.Stat(path.Dir(spath)); os.IsNotExist(err) {
		err = os.Mkdir(path.Dir(spath), 0755)
		if err != nil {
			return err
		}
	}

	f, err := os.OpenFile(spath, os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return err
	}
	defer f.Close()

	_, err = fmt.Fprintf(f, "%v", request.ID)
	if err != nil {
		return err
	}

	err = f.Sync()
	if err != nil {
		return err
	}

	return nil
}

func load(serviceName, cuuid string) (string, error) {
	spath := path.Join(storePath, serviceName, cuuid)

	f, err := os.Open(spath)
	if err != nil {
		return "", err
	}

	var out string
	_, err = fmt.Fscanf(f, "%s", &out)
	if err != nil {
		return "", err
	}

	return out, nil

}
