package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

var cfgFile string

// rootCmd represents the base command when called without any subcommands
var rootCmd = &cobra.Command{
	Use:   "turnt",
	Short: "Turnt is the client in the private network that retrieve request and replay them locally",
	Long: `
This application retrieve requests from the lower part of the diode and send them to the highest component (your private and protected API server)
This private API server is something on your network that you don't want to be publicly accessible. But you also need it to be able to receive requests from another network.

turnt is here to help you achieve this goal.`,
	// Uncomment the following line if your bare application
	// has an action associated with it:
	//	Run: func(cmd *cobra.Command, args []string) { },
}

// Execute adds all child commands to the root command and sets flags appropriately.
// This is called by main.main(). It only needs to happen once to the rootCmd.
func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

func init() {
	cobra.OnInitialize(initConfig)

}

// envDoc is the list of environment variable that you want to document
var envDoc map[string]string

func rc(key, env string, defVal interface{}, doc bool) {
	viper.BindEnv(key, env)
	viper.SetDefault(key, defVal)
	if doc {
		envDoc[env] = fmt.Sprintf("%v", defVal)
	}
}

// initConfig reads in config file and ENV variables if set.
func initConfig() {
	envDoc = make(map[string]string)

	rc("verbose", "VERBOSE", false, true)
	rc("consumer.secret_key", "CONSUMER_SECRET_KEY", "", true)
	rc("consumer.public_key", "CONSUMER_PUBLIC_KEY", "", true)
	rc("server.address", "SERVER_ADDRESS", "https://apiturntables.io", true)
	rc("destination.service.url", "DESTINATION_SERVICE_URL", "http://yourAPI.local/v1/test", true)
	rc("workers", "WORKERS", 4, true)

	var envUsage string
	envUsage += "\nConfigurable Environment variables:\n"
	for k, v := range envDoc {
		envUsage += fmt.Sprintf("  - %v (default: %q)\n", k, v)
	}

	rootCmd.SetUsageTemplate(rootCmd.UsageTemplate() + envUsage)

}
