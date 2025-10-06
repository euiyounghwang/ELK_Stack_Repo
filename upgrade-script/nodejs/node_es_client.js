
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
const indices_name = process.env.INDICES_NAME;

console.log(`\nenvInfo: ${env_desc}`);
console.log(`es_nodes_list: ${es_nodes_1},${es_nodes_2},${es_nodes_3}`);
console.log(`ca_certificate_path: ${caCertificate}`);
console.log(`username: ${username}`);
console.log(`password: ${password}`);
console.log(`indices_name: ${indices_name}`);

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


async function getSearchDocuments(index_name) {
  try {
    const { body } = await client.search({
      // index: 'your_index_name', // Replace with your index name
      index: index_name,
      body: {
        query: {
          // match: {
          //   your_field_name: 'search_term' // Replace with your field and search term
          // }
          match_all: {

          }
        }
      }
    });

    console.log('\n**')
    console.log(`Get_es_search [${username}]`)
    console.log('Search Results:', body.hits.hits);
  } catch (error) {
    console.error('Error during search:', error);
  } finally {
    console.log('**\n')
  }
}

async function getAllIndices() {
  try {
    const response = await client.cat.indices({ format: 'json' });
    // console.log('All Indices:', response);
    // console.log('All Indices:', response.body);
    // Parsing the information
    console.log('\n**')
    console.log(`List of Elasticsearch Indices with account: [${username}]`)
    let sb = [];
    for (const indexName in response.body) {
      sb.push(`${response.body[indexName]['index']},`);
      // if (Object.hasOwnProperty.call(response.body, indexName)) {
      //   const indexInfo = response.body[indexName];
      //   console.log(`\nIndex Name: ${indexName}`);
      //   console.log(`  UUID: ${indexInfo.settings.index.uuid}`);
      //   console.log(`  Number of Shards: ${indexInfo.settings.index.number_of_shards}`);
      //   console.log(`  Number of Replicas: ${indexInfo.settings.index.number_of_replicas}`);
      //   // You can access other properties like mappings, aliases, etc.
      //   // console.log('  Mappings:', indexInfo.mappings);
      // }
    }
    console.log(sb.join(''))
    console.log('**\n')
  } catch (error) {
    console.error('Error retrieving indices:', error);
  }
}

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

// es get all indices
getAllIndices();

// es search 
getSearchDocuments(indices_name)