package main

import (
	"fmt"
	"net/http"
	"os"
	"time"
)

func handler(w http.ResponseWriter, r *http.Request) {
	hostname, _ := os.Hostname()
	fmt.Fprintf(w, "Hello from %s\n", hostname)
}

func longHandler(w http.ResponseWriter, r *http.Request) {
	hostname, _ := os.Hostname()
	time.Sleep(10 * time.Second)
	fmt.Fprintf(w, "Hello! long running request finished from %s\n", hostname)
}

func main() {
	http.HandleFunc("/", handler)
	http.HandleFunc("/long", longHandler)
	http.ListenAndServe(":8081", nil)
}
