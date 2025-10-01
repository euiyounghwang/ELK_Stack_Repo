package repository

import "time"

type ES_Cluster_Info struct {
	Name        string `json:"name"`
	ClusterName string `json:"cluster_name"`
	ClusterUUID string `json:"cluster_uuid"`
	Version     struct {
		Number                           string    `json:"number"`
		BuildFlavor                      string    `json:"build_flavor"`
		BuildType                        string    `json:"build_type"`
		BuildHash                        string    `json:"build_hash"`
		BuildDate                        time.Time `json:"build_date"`
		BuildSnapshot                    bool      `json:"build_snapshot"`
		LuceneVersion                    string    `json:"lucene_version"`
		MinimumWireCompatibilityVersion  string    `json:"minimum_wire_compatibility_version"`
		MinimumIndexCompatibilityVersion string    `json:"minimum_index_compatibility_version"`
	} `json:"version"`
	Tagline string `json:"tagline"`
}

type ES_Cluster struct {
	ClusterName                 string  `json:"cluster_name"`
	Status                      string  `json:"status"`
	TimedOut                    bool    `json:"timed_out"`
	NumberOfNodes               int     `json:"number_of_nodes"`
	NumberOfDataNodes           int     `json:"number_of_data_nodes"`
	ActivePrimaryShards         int     `json:"active_primary_shards"`
	ActiveShards                int     `json:"active_shards"`
	RelocatingShards            int     `json:"relocating_shards"`
	InitializingShards          int     `json:"initializing_shards"`
	UnassignedShards            int     `json:"unassigned_shards"`
	DelayedUnassignedShards     int     `json:"delayed_unassigned_shards"`
	NumberOfPendingTasks        int     `json:"number_of_pending_tasks"`
	NumberOfInFlightFetch       int     `json:"number_of_in_flight_fetch"`
	TaskMaxWaitingInQueueMillis int     `json:"task_max_waiting_in_queue_millis"`
	ActiveShardsPercentAsNumber float64 `json:"active_shards_percent_as_number"`
}
