package utility

import (
	"fmt"
	"io/ioutil"
	"net/http"
)

func Get(url string) {
	response, err := http.Get(url)

	if err != nil {
		return
	}

	defer response.Body.Close()

	content, _ := ioutil.ReadAll(response.Body)
	fmt.Print(string(content))
}
