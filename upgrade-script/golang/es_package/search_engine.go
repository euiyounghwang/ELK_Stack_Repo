package es_package

import (
	"context"
	"crypto/x509"
	"encoding/json"
	"encoding/pem"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"strings"

	"es_upgrade/repository"
	"es_upgrade/utility"

	"github.com/elastic/go-elasticsearch/v7"
	"golang.org/x/text/language"
	"golang.org/x/text/message"
)

func Get_es_search(es *elasticsearch.Client, index_name string) {
	/*
		# Key check
		users := map[string]string{
		    "bob": "New York",
		    "lisa": "Japan",
		    "marco": "Italy",
		  }
		city, ok := users["bob"]
		if ok {
		    fmt.Println("bob lives in", city)
		} else {
		    fmt.Println("bob is not in the map")
		}
	*/

	fmt.Printf("\n**\n")
	fmt.Printf("Get_es_search [%s]\n", os.Getenv("BASIC_AUTH_USERNAME"))
	// fmt.Println(es.Info())

	// Perform a search query
	// Define a simple match_all query
	var buf strings.Builder
	buf.WriteString(`{"query":{"match_all":{}}}`)

	// Perform the search
	res, err := es.Search(
		es.Search.WithContext(context.Background()),
		es.Search.WithIndex(index_name),
		es.Search.WithBody(strings.NewReader(buf.String())),
		es.Search.WithTrackTotalHits(true), // Optional: to get total hits count
		es.Search.WithPretty(),             // Optional: for pretty-printed JSON response
	)

	if err != nil {
		log.Fatalf("Error getting response: %s", err)
	}

	p := message.NewPrinter(language.English)

	// Decode the JSON response
	var r map[string]interface{}
	if err := json.NewDecoder(res.Body).Decode(&r); err != nil {
		log.Fatalf("Error parsing the response body: %s", err)
	} else {
		// Access hits, aggregations, etc. from the 'r' map
		if r != nil {
			_, ok := r["hits"]
			if ok {
				p.Printf("\nTotal hits: %v\n", r["hits"].(map[string]interface{})["total"].(map[string]interface{})["value"])
				for _, hit := range r["hits"].(map[string]interface{})["hits"].([]interface{}) {
					source := hit.(map[string]interface{})["_source"]
					_id := hit.(map[string]interface{})["_id"]
					// fmt.Printf(" - Source: %v\n", source)
					fmt.Printf(" - _id: %s, source : %s\n", _id, source.(map[string]interface{})["ADDTS"])
				}
			} else {
				fmt.Println("No permission.")
			}
		}
		// fmt.Println("No hits found.")
	}

	fmt.Printf("**\n")
}

func Get_certificate_info(Cacert string) {
	// Replace "path/to/your/certificate.pem" with the actual path to your PEM file
	certPEMBlock, err := ioutil.ReadFile(Cacert)
	if err != nil {
		log.Fatalf("Failed to read certificate file: %v", err)
	}

	block, _ := pem.Decode(certPEMBlock)
	if block == nil || block.Type != "CERTIFICATE" {
		log.Fatal("Failed to decode PEM block containing certificate")
	}

	cert, err := x509.ParseCertificate(block.Bytes)
	if err != nil {
		log.Fatalf("Failed to parse certificate: %v", err)
	}

	fmt.Println("Certificate Subject:")
	fmt.Printf("cert.Issuer: %s\n", cert.Issuer)
	fmt.Printf("cert.SerialNumber: %s\n", cert.SerialNumber)
	fmt.Printf("Common Name (CN): %s\n", cert.Subject.CommonName)
	fmt.Printf("Organization (O): %v\n", cert.Subject.Organization)
	fmt.Printf("Organizational Unit (OU): %v\n", cert.Subject.OrganizationalUnit)
	fmt.Printf("Country (C): %v\n", cert.Subject.Country)
	fmt.Printf("State (ST): %v\n", cert.Subject.Province) // Note: Province is typically used for State
	fmt.Printf("Locality (L): %v\n", cert.Subject.Locality)
	fmt.Printf("Certificate Not Before (Issue Date): %s\n", cert.NotBefore.Format("2006-01-02 15:04:05"))
	fmt.Printf("Certificate Not After (Expiration Date): %s\n", cert.NotAfter.Format("2006-01-02 15:04:05"))
	fmt.Printf("\n")
}

func Get_es_indices(es *elasticsearch.Client) {
	fmt.Printf("\n**\n")
	fmt.Printf("List of Elasticsearch Indices with account: [%s]\n", os.Getenv("BASIC_AUTH_USERNAME"))

	res, err := es.Cat.Indices(es.Cat.Indices.WithFormat("json"))
	if err != nil {
		log.Println(err)
	}
	defer res.Body.Close()

	body, _ := ioutil.ReadAll(res.Body)

	// fmt.Print(utility.PrettyString(string(body)))

	response_map := repository.ES_Indices{}
	// log.Println(response_map)
	if err := json.Unmarshal(body, &response_map); err != nil {
		// do error check
		log.Println(err)
	}

	/*
		// Pretty-print the JSON
		// Converts the Go data structure back into a JSON string with indentation for pretty-printing.
		prettyJSON, err := json.MarshalIndent(response_map, "", "  ")
		if err != nil {
			log.Fatalf("Error pretty-printing JSON: %s", err)
		}

		fmt.Print(string(prettyJSON))
	*/
	// In Go, the strings.Builder type is used for efficient string construction and concatenation
	var sb strings.Builder
	for _, rows := range response_map {
		// fmt.Println(rows)
		// fmt.Printf("%s, ", rows.Index)
		sb.WriteString(fmt.Sprintf("%s,", rows.Index))
	}
	fmt.Print(utility.Build_split_string_array(sb.String()))
	fmt.Printf("\n**\n")
}

func Get_es_info(es *elasticsearch.Client) {
	/*
		// Ping the cluster to verify connection
		res, err := es.Info()
		if err != nil {
			log.Fatalf("Error getting response: %s", err)
		}
		defer res.Body.Close()
	*/

	// Constructs a request to the _cat/indices API, specifying that the response should be in JSON format.
	res, err := es.Cluster.Health(es.Cluster.Health.WithPretty()) // WithPretty() for formatted output
	if err != nil {
		// Handle error
	}
	defer res.Body.Close()

	fmt.Printf("**\n")
	output := fmt.Sprintf("Successfully connected to Elasticsearch! [%s]\n", os.Getenv("ES_NODE_1"))
	fmt.Print(output)
	// fmt.Printf("**\n")
	body, _ := ioutil.ReadAll(res.Body)
	// fmt.Println(string(body))

	response_map := repository.ES_Cluster{}
	// Parses the JSON response into a Go slice of maps, where each map represents an index and its properties.
	if err := json.Unmarshal(body, &response_map); err != nil {
		// do error check
		log.Println(err)
	}

	// for i, rows := range response_map. {
	// }
	fmt.Printf("Cluster Name: %s\n", response_map.ClusterName)
	fmt.Printf("Cluster Health: %s\n", response_map.Status)
	fmt.Printf("Number of Nodes: %d\n", response_map.NumberOfNodes)
	fmt.Printf("Active Shards: %d\n", response_map.ActiveShards)
	fmt.Printf("Relocating Shards: %d\n", response_map.RelocatingShards)
	fmt.Printf("ActiveShardsPercentAsNumber: %.2f\n", response_map.ActiveShardsPercentAsNumber)
}

func Get_elasticsearch() *elasticsearch.Client {
	// Load the CA certificate
	caCert, err := ioutil.ReadFile(os.Getenv("CERT_PATH"))
	if err != nil {
		log.Fatalf("Error reading CA certificate: %s", err)
	}

	// Configure the Elasticsearch client
	cfg := elasticsearch.Config{
		Addresses: []string{
			os.Getenv("ES_NODE_1"),
			os.Getenv("ES_NODE_2"),
			os.Getenv("ES_NODE_3"),
		},
		// Add other configurations like username/password if needed
		Username: os.Getenv("BASIC_AUTH_USERNAME"),
		Password: os.Getenv("BASIC_AUTH_PASSWORD"),
		CACert:   caCert,
		// Transport: &http.Transport{
		// 	MaxIdleConnsPerHost:   10,
		// 	ResponseHeaderTimeout: time.Second,
		// 	DialContext:           (&net.Dialer{Timeout: time.Second}).DialContext,
		// 	TLSClientConfig: &tls.Config{
		// 		MinVersion:         tls.VersionTLS12,
		// 		InsecureSkipVerify: true,
		// 	},
		// },
	}

	// Creates a new Elasticsearch client.
	es, err := elasticsearch.NewClient(cfg)
	if err != nil {
		log.Fatalf("Error creating the client: %s", err)
	}

	return es

	/*
		// 2. Index a document
		article := Article{
			Title:   "Go and Elasticsearch Integration",
			Content: "This article demonstrates how to use the Go client for Elasticsearch to perform basic operations.",
			Author:  "Go Developer",
		}
		articleJSON, err := json.Marshal(article)
		if err != nil {
			log.Fatalf("Error marshaling article: %s", err)
		}

		req := esapi.IndexRequest{
			Index:      "my_articles", // Index name
			DocumentID: "1",           // Document ID (optional, Elasticsearch can generate one)
			Body:       strings.NewReader(string(articleJSON)),
			Refresh:    "true", // Make the document immediately searchable
		}

		indexRes, err := req.Do(context.Background(), es)
		if err != nil {
			log.Fatalf("Error indexing document: %s", err)
		}
		defer indexRes.Body.Close()
		if indexRes.IsError() {
			log.Fatalf("Error indexing document: %s", indexRes.String())
		}
		fmt.Println("Document indexed successfully!")

		// 3. Perform a search
		searchQuery := `{
			"query": {
				"match": {
					"content": "Go client"
				}
			}
		}`

		searchReq := esapi.SearchRequest{
			Index: []string{"my_articles"},
			Body:  strings.NewReader(searchQuery),
		}

		searchRes, err := searchReq.Do(context.Background(), es)
		if err != nil {
			log.Fatalf("Error performing search: %s", err)
		}
		defer searchRes.Body.Close()

		if searchRes.IsError() {
			log.Fatalf("Error searching documents: %s", searchRes.String())
		}

		var r map[string]interface{}
		if err := json.NewDecoder(searchRes.Body).Decode(&r); err != nil {
			log.Fatalf("Error parsing the response body: %s", err)
		}

		fmt.Println("\nSearch Results:")
		for _, hit := range r["hits"].(map[string]interface{})["hits"].([]interface{}) {
			source := hit.(map[string]interface{})["_source"]
			fmt.Printf("  Title: %s, Author: %s\n", source.(map[string]interface{})["title"], source.(map[string]interface{})["author"])
		}
	*/
}
