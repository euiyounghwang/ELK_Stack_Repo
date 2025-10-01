package es_package

import (
	"fmt"
	"io/ioutil"
	"log"
	"os"

	"github.com/elastic/go-elasticsearch/v7"
)

func Get_es_search(es *elasticsearch.Client) {
	fmt.Printf("**\n")
	fmt.Printf("Get_es_search")
	// fmt.Println(es.Info())
	fmt.Printf("**\n")
}

func Get_es_info(es *elasticsearch.Client) {
	// Ping the cluster to verify connection
	res, err := es.Info()
	if err != nil {
		log.Fatalf("Error getting response: %s", err)
	}
	defer res.Body.Close()

	fmt.Printf("**\n")
	output := fmt.Sprintf("Successfully connected to Elasticsearch! [%s]\n", os.Getenv("BASIC_AUTH_USERNAME"))
	fmt.Print(output)
	fmt.Printf("**\n")
	body, _ := ioutil.ReadAll(res.Body)
	fmt.Println(string(body))
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
	}

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
