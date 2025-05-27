using Elasticsearch.Net;
using Nest;
using System.Security.Cryptography.X509Certificates;
 
namespace elasticsearch_client_example
{
    public class Testing
    {
        public string Description;
        public DateTime Timestamp;
 
        public Testing(string Description, DateTime Timestamp)
        {
            this.Description = Description;
            this.Timestamp = Timestamp;
        }
    }
 
    /* https://www.instaclustr.com/support/documentation/elasticsearch/using-elasticsearch/connecting-to-elasticsearch-with-c-sharp/ */
    public class Client
    {
        static void Main(string[] args)
        {
            var cert = new X509Certificate("/path/to/cluster-ca-certificate.pem");

            var uris = new Uri[]
            {
                new Uri("https://xxx.xxx.xxx.xxx:9200"),
                new Uri("https://xxx.xxx.xxx.xxx:9200"),
                new Uri("https://xxx.xxx.xxx.xxx:9200")
            };


            var connectionPool = new SniffingConnectionPool(uris);
            var settings = new ConnectionSettings(connectionPool)
                .BasicAuthentication("icelasticsearch", "<Password>")
                .ServerCertificateValidationCallback(
                    CertificateValidations.AuthorityIsRoot(cert)
                )
                .DefaultMappingFor<Testing>(i => i.IndexName("testing"));

            var client = new ElasticClient(settings);

            var document = new Testing("this is a test", DateTime.Now);

            var indexResponse = client.Index(new IndexRequest<Testing>(document, IndexName.From<Testing>(), 1));
            if (!indexResponse.IsValid)
            {
                Console.Write("Failed to index document. ");
                if (indexResponse.ServerError != null)
                {
                    Console.WriteLine(indexResponse.ServerError);
                }
                else if (indexResponse.OriginalException != null)
                {
                    Console.WriteLine(indexResponse.OriginalException);
                }
                else
                {
                    Console.WriteLine("Error code: " + indexResponse.ApiCall.HttpStatusCode);
                }
            }
            else
            {
                Console.WriteLine($"Indexed document to index \"testing\" with id 1");
            }


            var getResponse = client.Get<Testing>(new GetRequest<Testing>(1));
            if (getResponse.OriginalException != null)
            {
                throw getResponse.OriginalException;
            }

            if (!getResponse.IsValid)
            {
                Console.Write("Failed to retrieve document. ");
                if (getResponse.ServerError != null)
                {
                    Console.WriteLine(getResponse.ServerError);
                }
                else if (getResponse.OriginalException != null)
                {
                    Console.WriteLine(getResponse.OriginalException);
                }
                else
                {
                    Console.WriteLine("Error code: " + getResponse.ApiCall.HttpStatusCode);
                }
            }
            else
            {
                Console.WriteLine($"Retrieved document: " +
                    $"{{Id: {getResponse.Id}, " +
                    $"Description: {getResponse.Source.Description}, " +
                    $"Timestamp: {getResponse.Source.Timestamp}}}");
            }
        }
    }
}