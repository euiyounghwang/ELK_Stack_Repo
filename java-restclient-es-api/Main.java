package com.example;

import org.apache.http.HttpHost;
import org.apache.http.auth.AuthScope;
import org.apache.http.auth.UsernamePasswordCredentials;
import org.apache.http.client.CredentialsProvider;
import org.apache.http.impl.client.BasicCredentialsProvider;
import org.apache.http.impl.nio.client.HttpAsyncClientBuilder;
import org.apache.http.ssl.SSLContextBuilder;
import org.apache.http.ssl.SSLContexts;
import org.opensearch.action.admin.indices.delete.DeleteIndexRequest;
import org.opensearch.action.delete.DeleteRequest;
import org.opensearch.action.delete.DeleteResponse;
import org.opensearch.action.get.GetRequest;
import org.opensearch.action.get.GetResponse;
import org.opensearch.action.index.IndexRequest;
import org.opensearch.action.index.IndexResponse;
import org.opensearch.action.support.master.AcknowledgedResponse;
import org.opensearch.client.RequestOptions;
import org.opensearch.client.RestClient;
import org.opensearch.client.RestClientBuilder;
import org.opensearch.client.RestHighLevelClient;
import org.opensearch.client.indices.CreateIndexRequest;
import org.opensearch.client.indices.CreateIndexResponse;
import org.opensearch.common.settings.Settings;
import org.opensearch.client.sniff.SniffOnFailureListener;
import org.opensearch.client.sniff.OpenSearchNodesSniffer;
import org.opensearch.client.sniff.NodesSniffer;
import org.opensearch.client.sniff.Sniffer;
import javax.net.ssl.SSLContext;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.KeyManagementException;
import java.security.KeyStore;
import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;
import java.security.cert.CertificateException;
import java.util.HashMap;
import java.util.concurrent.TimeUnit;
 
// https://www.restack.io/p/java-elasticsearch-client-answer-ssl-configuration
// Import the CA Certificate: Use the Java keytool to import the CA certificate into a Java KeyStore (JKS). This is essential for establishing a secure connection. The command is as follows:
// keytool -import -alias elasticsearch-ca -file http_ca.crt -keystore elasticsearch.jks -storepass changeit
public class Main {
    public static void main(String[] args)  throws IOException, KeyStoreException, NoSuchAlgorithmException, KeyManagementException {
        final CredentialsProvider credentialsProvider = new BasicCredentialsProvider();
        credentialsProvider.setCredentials(AuthScope.ANY, new UsernamePasswordCredentials("test", "test"));
 
        Path trustStorePath = Paths.get("./test.jks");
        KeyStore truststore = KeyStore.getInstance("jks");
        try (InputStream is = Files.newInputStream(trustStorePath)) {
            truststore.load(is, "test".toCharArray());
        } catch (CertificateException e) {
            e.printStackTrace();
        }
        SSLContextBuilder sslBuilder = SSLContexts.custom().loadTrustMaterial(truststore, null);
        final SSLContext sslContext = sslBuilder.build();
        RestClientBuilder builder = RestClient.builder(
            new HttpHost("localhost", 9200, "https"))
            // new HttpHost("xxx.xxx.xxx.xxx", 9200, "https"),
            // new HttpHost("xxx.xxx.xxx.xxx", 9200, "https"))
            .setHttpClientConfigCallback(new RestClientBuilder.HttpClientConfigCallback() {
                public HttpAsyncClientBuilder customizeHttpClient(
                  final HttpAsyncClientBuilder httpAsyncClientBuilder) {
                      return httpAsyncClientBuilder.setDefaultCredentialsProvider(credentialsProvider).setSSLContext(sslContext);
                  }
          });
 
        RestHighLevelClient client = new RestHighLevelClient(builder);
 
        NodesSniffer nodesniffer = new OpenSearchNodesSniffer (
                client.getLowLevelClient(),
                TimeUnit.SECONDS.toMillis(5),
                OpenSearchNodesSniffer.Scheme.HTTPS);
 
        Sniffer sniffer = Sniffer.builder(client.getLowLevelClient())
                .setNodesSniffer(nodesniffer)
                .build();
 
        SniffOnFailureListener listener = new SniffOnFailureListener();
        listener.setSniffer(sniffer);
 
        try {
            String index = "java-test-index";
            CreateIndexRequest createIndexRequest = new CreateIndexRequest(index);
     
            createIndexRequest.settings(Settings.builder()
                .put("index.number_of_shards", 5)
                .put("index.number_of_replicas", 1)
            );
     
            HashMap<String, String> typeMapping = new HashMap<String,String>();
            typeMapping.put("type", "integer");
            HashMap<String, Object> ageMapping = new HashMap<String, Object>();
            ageMapping.put("age", typeMapping);
            HashMap<String, Object> mapping = new HashMap<String, Object>();
            mapping.put("properties", ageMapping);
            createIndexRequest.mapping(mapping);
            CreateIndexResponse createIndexResponse = client.indices().create(createIndexRequest, RequestOptions.DEFAULT);
            System.out.println("\nCreating index:");
            System.out.println("Is client acknowledged?" + ((createIndexResponse.isAcknowledged())? " Yes" : " No"));
     
            // IndexRequest request = new IndexRequest(index);
            // request.id("1");
     
            // HashMap<String, String> stringMapping = new HashMap<String, String>();
            // stringMapping.put("message:", "Testing Java REST client");
            // request.source(stringMapping);
            // IndexResponse indexResponse = client.index(request, RequestOptions.DEFAULT);
            // System.out.println("\nAdding document:");
            // // System.out.println(indexResponse);
     
            // GetRequest getRequest = new GetRequest(index, "1");
            // GetResponse response = client.get(getRequest, RequestOptions.DEFAULT);
            // System.out.println("\nSearch results:");
            // System.out.println(response.getSourceAsString());
     
            // DeleteRequest deleteDocumentRequest = new DeleteRequest(index, "1");
            // DeleteResponse deleteResponse = client.delete(deleteDocumentRequest, RequestOptions.DEFAULT);
            // System.out.println("\nDeleting document:");
            // System.out.println(deleteResponse);
     
            DeleteIndexRequest deleteIndexRequest = new DeleteIndexRequest(index);
            AcknowledgedResponse deleteIndexResponse = client.indices().delete(deleteIndexRequest, RequestOptions.DEFAULT);
            System.out.println("\nDeleting index:");
            System.out.println("Is client acknowledged?" + ((deleteIndexResponse.isAcknowledged())? " Yes" : " No"));
        } catch (Exception e) {
            // TODO: handle exception
            System.out.println(e);
        }
        finally {
            client.close();
        }
    }
}