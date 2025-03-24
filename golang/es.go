package main

import (
	"crypto/tls"
	"fmt"
	"log"
	"net"
	"net/http"
	"os"
	"time"

	"github.com/elastic/go-elasticsearch/v8"
	"github.com/joho/godotenv"
)

// https://github.com/euiyounghwang/go-search_engine/blob/master/tools/elasticsearch_api.go
// https://eblo.tistory.com/249
// https://github.com/elastic/go-elasticsearch/issues/86
func main() {

	log.SetFlags(0)

	// https://www.linkedin.com/pulse/how-read-env-files-golang-fabio-lima-wlcdf/
	err := godotenv.Load("../.env")
	if err != nil {
		log.Fatalf("Error loading .env file: %s", err)
	}

	cfg := elasticsearch.Config{
		Addresses: []string{
			// "https://localhost1:9200", "https://localhost2:9200", "https://localhost3:9200",
			os.Getenv("es_host_0"), os.Getenv("es_host_1"), os.Getenv("es_host_2"),
		},
		// Username: "es_admin",
		Username: os.Getenv("username"),
		Password: os.Getenv("password"),
		Transport: &http.Transport{
			MaxIdleConnsPerHost:   10,
			ResponseHeaderTimeout: time.Second,
			DialContext:           (&net.Dialer{Timeout: time.Second}).DialContext,
			TLSClientConfig: &tls.Config{
				MinVersion:         tls.VersionTLS12,
				InsecureSkipVerify: true,
			},
		},
	}

	es, err := elasticsearch.NewClient(cfg)
	if err != nil {
		log.Fatalf("Error getting response: %s", err)
	}

	res, err := es.Info()
	if err != nil {
		log.Fatalf("Error getting response: %s", err)
	}

	defer res.Body.Close()

	// Check response status
	if res.IsError() {
		log.Fatalf("Error: %s", res.String())
	}

	// Print client and server version numbers.
	log.Printf("Client: %s", elasticsearch.Version)
	// log.Println(strings.Repeat("~", 37))

	// res, err := esapi.CatIndicesRequest{Format: "json"}.Do(context.Background(), es)
	// if err != nil {
	// 	return
	// }

	// fmt.Println(res.String())
	fmt.Println(res)
	// manifestJson, _ := json.MarshalIndent(res, "", "  ")

	// log.Println(string(manifestJson))

	// defer res.Body.Close()

}
