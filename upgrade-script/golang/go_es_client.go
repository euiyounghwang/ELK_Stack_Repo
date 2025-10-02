package main

import (
	"log"
	"os"

	es_instance "es_upgrade/es_package"

	"github.com/joho/godotenv"
)

// Article represents a document to be stored in Elasticsearch
type Article struct {
	Title   string `json:"title"`
	Content string `json:"content"`
	Author  string `json:"author"`
}

func main() {
	// Load .env from a specific path
	err := godotenv.Load("../csharp/esclient/.env")
	if err != nil {
		log.Fatalf("Error loading .env file: %s", err)
	}

	es_client := es_instance.Get_elasticsearch()

	// es certificate info
	es_instance.Get_certificate_info(os.Getenv("CERT_PATH"))

	// es info
	es_instance.Get_es_info(es_client)

	// es cat/indices
	es_instance.Get_es_indices(es_client)

	// es search
	es_instance.Get_es_search(es_client)
}
