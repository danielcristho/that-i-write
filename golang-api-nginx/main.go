package main

import (
	"fmt"
	"net/http"

	"github.com/common-nighthawk/go-figure"
)

func handler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/plain")
	asciiArt := figure.NewFigure("Simple Go API", "", true).String()
	fmt.Fprintln(w, asciiArt)
}

func main() {
	http.HandleFunc("/", handler)
	fmt.Println("Server started at :8080")
	http.ListenAndServe(":8080", nil)
}
