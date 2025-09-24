

/*
The most common cause of a thumbprint mismatch is that C# code and Elasticsearch were configured to use different hasing algorithm.
X509Certificate2.Thumbprint in C#: By default, the X509Certificate2.Thumbprint property uses the SHA-1 algorithm to compute the hash. 
This is a legacy algorithm and may not be what your Elasticsearch cluster is using.

https://www.google.com/search?q=X509Certificate2.Thumbprint+c%23+different+hasing+algorithm&sca_esv=879ff1ce65093d89&rlz=1C1GCEB_enUS1102US1102&sxsrf=AE3TifOOMNTKc338lbyogz0PVSDE99iiIA%3A1758550402293&ei=glnRaMbUEf7S5NoP4a7XkAQ&ved=0ahUKEwjGnbHgxuyPAxV-KVkFHWHXFUIQ4dUDCBA&uact=5&oq=X509Certificate2.Thumbprint+c%23+different+hasing+algorithm&gs_lp=Egxnd3Mtd2l6LXNlcnAiOVg1MDlDZXJ0aWZpY2F0ZTIuVGh1bWJwcmludCBjIyBkaWZmZXJlbnQgaGFzaW5nIGFsZ29yaXRobTIFEAAY7wUyCBAAGIAEGKIEMgUQABjvBTIFEAAY7wUyCBAAGIAEGKIESOwUUABYkxJwAHgAkAEAmAGyAaAB-gOqAQMwLjO4AQPIAQD4AQL4AQGYAgOgAosEmAMAkgcDMC4zoAfvDrIHAzAuM7gHiwTCBwcwLjIuMC4xyAcO&sclient=gws-wiz-serp

The X509Certificate2.Thumbprint property in C# always returns the SHA-1 hash of the certificate. This behavior is for legacy reasons and is hardcoded within the .NET framework.
To obtain the hash of an X509Certificate2 object using a different hashing algorithm (e.g., SHA256, SHA384, SHA512), use the GetCertHashString(HashAlgorithmName) method or the GetCertHash(HashAlgorithmName) method.

openssl x509 -in ./dev-es8-ca.pem -noout -fingerprint -sha256

*/

using Nest;
using System;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Collections.Generic;
using Elasticsearch.Net;
using Elastic.Clients.Elasticsearch;
using Elastic.Transport;
using DotNetEnv;

// dotnet new console
// dotnet add package NEST --version 7.17.4
// dotnet add package DotNetEnv
public class ElasticsearchConnection
{
    // dotnet add package Elastic.Clients.Elasticsearch --version 7.17.4
    /*
    public static void get_ElasticsearchClientSettings()
    {
        // Replace with your Elasticsearch URL
        // var uri = new Uri("https://your-elasticsearch-host:9200"); 
        var nodes = new Uri[]
        {
            new Uri(Env.GetString("ES_NODE_1")),
            new Uri(Env.GetString("ES_NODE_2")),
            new Uri(Env.GetString("ES_NODE_3"))
        };


        var connectionPool = new Uri(Env.GetString("ES_NODE_1"));
        // var connectionPool = new StaticConnectionPool(nodes);

        // Replace with your username and password for basic authentication
        var username = Env.GetString("BASIC_AUTH_USERNAME");
        var password = Env.GetString("BASIC_AUTH_PASSWORD");


        // Replace with the path to your CA certificate file (e.g., in PEM format)
        // var caCertPath = @$"{Env.GetString("CERT_PATH")}\dev\dev-es8-ca.pem";

        var settings = new ElasticsearchClientSettings(new Uri(connectionPool))
            .Authentication(new BasicAuthentication(username, password))
            // .ClientCertificate(caCert)
            .ServerCertificateValidationCallback((sender, certificate, chain, sslPolicyErrors) =>
            {

                // Load the CA certificate
                // var caCert = new X509Certificate2(caCertPath);
                // X509Certificate2 local_certi = new X509Certificate2(caCertPath);

                // Build a chain for the server certificate
                // var certChain = new X509Chain();
                // certChain.Build(certificate as X509Certificate2);

                // Check if the server certificate is issued by the trusted CA
                // foreach (var element in certChain.ChainElements)
                // {
                //     // server_sha256 = caCert.GetCertHashString(HashAlgorithmName.SHA256);
                //     // if (element.Certificate.Thumbprint == caCert.Thumbprint)
                //     Console.WriteLine($"certChain.ChainElements.Count : {certChain.ChainElements.Count}");
                //     Console.WriteLine($"Local certification : {caCert.GetCertHashString(HashAlgorithmName.SHA256)}");
                //     Console.WriteLine($"Remote certification : {element.Certificate.GetCertHashString(HashAlgorithmName.SHA256)}");

                //     // if (element.Certificate.Thumbprint == caCert.GetCertHashString(HashAlgorithmName.SHA256))
                //     // {
                //     //     return true; // Certificate is trusted
                //     // }

                // }
                // return false; // Certificate is not trusted or validation failed

                // Load the CA certificate
                var caCert = new X509Certificate2(caCertPath);

                // Check if the server certificate is issued by the trusted CA
                // Check if the certificate from the remote secure ES cluster is the expected CA 
                if (certificate.Issuer == caCert.Subject)
                {
                    Console.WriteLine($"caCert.Subject : {caCert.Subject}");
                    return true;
                }

                return false; // Reject if validation fails

            });


        // Create the Elasticsearch client
        var client = new ElasticsearchClient(settings);

        // Example: Ping the cluster to verify connection
        var response = client.Ping();

        if (response.IsSuccess())
        {
            Console.WriteLine("Successfully connected to Elasticsearch!");
        }
        else
        {
            Console.WriteLine($"Failed to connect to Elasticsearch: {response.DebugInformation}");
        }
    }
    */

    public static void get_ConnectionSettings()
    {
        // Replace with your Elasticsearch URL
        // var uri = new Uri("https://your-elasticsearch-host:9200"); 
        var nodes = new Uri[]
        {
            new Uri(Env.GetString("ES_NODE_1")),
            new Uri(Env.GetString("ES_NODE_2")),
            new Uri(Env.GetString("ES_NODE_3"))
        };


        var connectionPool = new Uri(Env.GetString("ES_NODE_1"));
        // var connectionPool = new StaticConnectionPool(nodes);

        // Replace with your username and password for basic authentication
        var username = Env.GetString("BASIC_AUTH_USERNAME");
        var password = Env.GetString("BASIC_AUTH_PASSWORD");

        // Replace with the path to your CA certificate file (e.g., in PEM format)
        var caCertPath = @$"{Env.GetString("CERT_PATH")}\dev\dev-es8-ca.pem";
        // var caCertPath = @$"{Env.GetString("CERT_PATH")}\qa13_new\qa13-es8-ca.pem";
        
        // C# application can be configured to use specific node certificates for secure communication with your Elasticsearch cluster.
        // var node1CertPath = @$"{Env.GetString("CERT_PATH")}\dev\dev-node-1.pem";
        // var node2CertPath = @$"{Env.GetString("CERT_PATH")}\dev\dev-node-2.pem";
        // var node3CertPath = @$"{Env.GetString("CERT_PATH")}\dev\dev-node-3.pem";

        // var settings = new ConnectionSettings(connectionPool)
        //   .BasicAuthentication(username, password)
        //   .ServerCertificateValidationCallback((sender, certificate, chain, sslPolicyErrors) => true);

        // Create ConnectionSettings with basic authentication and CA certificate
        var settings = new ConnectionSettings(connectionPool)
            // .EnableApiCompatibilityMode() // This is the key for compatibility
            .BasicAuthentication(username, password)
            .ServerCertificateValidationCallback((sender, certificate, chain, sslPolicyErrors) =>
            {
                // The ServerCertificateValidationCallback is crucial for validating the server's certificate against your trusted CA

                // var node1Cert = new X509Certificate2(node1CertPath);
                // var node2Cert = new X509Certificate2(node2CertPath);
                // var node3Cert = new X509Certificate2(node3CertPath);

                // // Build a chain for the server certificate
                // var certChain = new X509Chain();
                // certChain.Build(certificate as X509Certificate2);

                // foreach (var element in certChain.ChainElements)
                // {

                //     // Console.WriteLine($"certChain.ChainElements.Count : {certChain.ChainElements.Count}");
                //     // Console.WriteLine($"Local certification : {node1Cert.GetCertHashString(HashAlgorithmName.SHA256)}");

                //     // The X509Certificate2.Thumbprint property in C# always returns the SHA-1 hash of the certificate. 
                //     // But the certificates are generated with SHA-256 Algoritm in Elasticsearh
                //     // Required to convert remote node certificate with SHA256 Algorithm
                //     var remote_certs = element.Certificate.GetCertHashString(HashAlgorithmName.SHA256);
                //     // if (element.Certificate.Thumbprint == caCert.Thumbprint)
                //     if (
                //         remote_certs == node1Cert.GetCertHashString(HashAlgorithmName.SHA256) ||
                //         remote_certs == node2Cert.GetCertHashString(HashAlgorithmName.SHA256) ||
                //         remote_certs == node3Cert.GetCertHashString(HashAlgorithmName.SHA256))
                //     {
                //         // Console.WriteLine($"Local certification : {node_certs}");
                //         // Console.WriteLine($"Remote certification : {remote_certs}");
                //         return true; // Certificate is trusted
                //     }

                //     // certChain.ChainPolicy.ExtraStore.Add(caCert);
                //     // return certChain.Build(new X509Certificate2(certificate));
                // }

                // Custom validation logic, e.g., checking if the certificate is signed by your CA
                // For self-signed or custom CA, you might need to manually validate the chain
                // or trust the specific CA certificate.
                // Example:
                // if (sslPolicyErrors == System.Net.Security.SslPolicyErrors.None)
                // {
                //     return true;
                // }

                // Load the CA certificate
                var caCert = new X509Certificate2(caCertPath);

                // By default, the X509Certificate2.Thumbprint property uses the SHA-1 algorithm to compute the hash. 
                // The X509Certificate2.Thumbprint property in C# explicitly returns the SHA-1 hash of the certificate. But elasticsearch returns SHA-2 has of the certificate.
                // Insteady of the Thumbprint property, we can add the below logic to compare the certifcate between local ca certicate and remote ES cluster's certs

                // Distinguished name (DN) is a term that describes the identifying information in a certificate and is part of the certificate itself.
                // Check if the certificate from the remote secure ES cluster is the expected CA 
                if (certificate.Issuer == caCert.Subject)
                {
                    return true;
                }

                return false; // Reject if validation fails
            });

        // Create the Elasticsearch client
        var client = new ElasticClient(settings);

        // Example: Ping the cluster to verify connection
        var response = client.Ping();

        if (response.IsValid)
        {
            Console.WriteLine("\n**");
            Console.WriteLine($"Successfully connected to Elasticsearch! [{connectionPool}]");

            try
            {
                var healthResponse = client.Cluster.Health();
                if (healthResponse.IsValid)
                {
                    Console.WriteLine($"Cluster Health API: {healthResponse}");
                    Console.WriteLine($"Cluster Name: {healthResponse.ClusterName}");
                    Console.WriteLine($"Cluster Health: {healthResponse.Status}");
                    Console.WriteLine($"Number of Nodes: {healthResponse.NumberOfNodes}");
                    Console.WriteLine($"Active Shards: {healthResponse.ActiveShards}");
                    Console.WriteLine($"Relocating Shards: {healthResponse.RelocatingShards}");
                    Console.WriteLine($"ActiveShardsPercentAsNumber: {healthResponse.ActiveShardsPercentAsNumber}%");
                }
                else
                {
                    Console.WriteLine($"Failed to get cluster health: {healthResponse.DebugInformation}");
                }

                /*
                CatResponse<CatIndicesRecord> catIndicesResponse = client.Cat.Indices();
                if (catIndicesResponse.IsValid)
                {
                    var indexNames = catIndicesResponse.Records.Select(record => record.Index).ToList();

                    Console.WriteLine($"List of Elasticsearch Indices with account: {username}");
                    foreach (var indexName in indexNames)
                    {
                        Console.WriteLine($"- {indexName}");
                    }
                }
                else
                {
                    Console.WriteLine($"Error retrieving indices: {catIndicesResponse.DebugInformation}");
                }
                */
            }
            catch (Exception ex)
            {
                Console.WriteLine($"An error occurred: {ex.Message}");
            }
        }
        else
        {
            Console.WriteLine($"Failed to connect to Elasticsearch: {response.DebugInformation}");
        }
        Console.WriteLine("**");
    }

    public static void Main(string[] args)
    {
        // dotnet add package DotNetEnv
        Env.Load(); // Loads .env from the current directory

        get_ConnectionSettings();
        // get_ElasticsearchClientSettings();
    }
}
