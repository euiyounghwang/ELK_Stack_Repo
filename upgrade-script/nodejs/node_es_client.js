
const { Client } = require('@elastic/elasticsearch');
const fs = require('fs');
const path = require('path');

// load .env file from csharp proj
require('dotenv').config({ path: '../csharp/esclient/.env' });

const env_desc = process.env.envInfo;
const es_nodes_1 = process.env.ES_NODE_1;
const es_nodes_2 = process.env.ES_NODE_2;
const es_nodes_3 = process.env.ES_NODE_3;
const caCertificate = process.env.CERT_PATH;
const username = process.env.BASIC_AUTH_USERNAME;
const password = process.env.BASIC_AUTH_PASSWORD;

console.log(`\nenvInfo: ${env_desc}`);
console.log(`es_nodes_list: ${es_nodes_1},${es_nodes_2},${es_nodes_3}`);
console.log(`ca_certificate_path: ${caCertificate}`);
console.log(`username: ${username}`);
console.log(`password: ${password}`);

// Read the CA certificate content
const caCert = fs.readFileSync(caCertificate, 'utf8');

// Create a new Elasticsearch client instance
const client = new Client({
        nodes: [
            es_nodes_1,
            es_nodes_2,
            es_nodes_3,
        ],
        auth: {
            username: username,
            password: password,
        },
        ssl: {
            ca: caCert, // Provide the CA certificate here
            // If you are using a self-signed certificate and want to bypass strict validation
            // for development purposes (NOT recommended for production):
            // rejectUnauthorized: false, 
        },
});

async function getCertificateInfo() {
  try 
    {
      const crypto = require("crypto")
      const cert = new crypto.X509Certificate(fs.readFileSync(caCertificate, 'utf8'))

      // console.log(cert)
      console.log("Certificate Subject:")
      // console.log(`cert.Issuer: ${cert.issuer}`)
      console.log(`cert.SerialNumber: ${cert.serialNumber}`)
      console.log(`cert.subject: ${cert.subject}`)
      console.log(`Certificate Not Before (Issue Date): ${cert.validFrom}`)
      console.log(`Certificate Not After (Expiration Date): ${cert.validTo}`)
    } catch (error) {
        console.error('Error getting cluster health:', error);
    } finally {
        // await client.close(); // Close the client connection
    }
}

// --- Main connection logic ---
async function getClusterConnect() {
  try 
  {
    // Test the connection
    const info = await client.info();
    // console.log('\nDetailed Health Information:', info.body);
    console.log('\n**');
    console.log(`Successfully connected to Elasticsearch! [${es_nodes_1}]`);
    // console.log('\Cluster Name:', info.body.cluster_name);
    // console.log('\Cluster Health:', info.body.status);
    // console.log('**');
    // console.log('\n');

    // Example: Perform a search
    /*
    const searchResult = await client.search({
      index: 'your_index_name', // Replace with your index name
      body: {
        query: {
          match_all: {},
        },
      },
    });
    console.log('Search results:', searchResult.body.hits.hits);
    */

  } catch (error) {
    console.error('Error connecting to Elasticsearch:', error);
  }
  finally {
     await client.close(); // Close the client connection
  }
}

async function getClusterHealth() {
    try 
    {
        const response = await client.cluster.health();
        // console.log('\nDetailed Health Information:', response.body);
        console.log('Cluster Health:', response.body.status);
        console.log('Number of Nodes:', response.body.number_of_nodes);
        console.log('Active Shards:', response.body.active_shards);
        console.log('Relocating Shards:', response.body.relocating_shards);
        console.log('ActiveShardsPercentAsNumber:', response.body.active_shards_percent_as_number);
        console.log('**');
        
    } catch (error) {
        console.error('Error getting cluster health:', error);
    } finally {
        await client.close(); // Close the client connection
    }
}

// es certificate info
getCertificateInfo();

// es connection
getClusterConnect();

// es info
getClusterHealth();