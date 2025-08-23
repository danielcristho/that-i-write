# Exploring Load Balancing in Caddy Using Docker

![Cover Images](https://res.cloudinary.com/diunivf9n/image/upload/v1755923140/caddy-lb-docker_peicwm.png)

Hello there! In this post, we'll dive more deep about Caddy, a modern and powerful web-server. Build using Go, Caddy offers a range of built-in-features, including **reverse proxy** and **load balancing**.

BTW, in this project I'll use **Caddy 2**, the latest version, which comes with a completely rewrittesn architecture and enhanced features. To make our setup and testing as smooth as possible, we'll leverage Docker. Docker allows us to easily create a reprodicible environment with all the necessary components.

The main focus of this post will be on understading and experimenting with Caddy's **load balancing algorithms**. We'll explore how Caddy intelligently distributes incomiing traffic, the different strategies it offers (such as **Round Robin**, **Least Connection**, **Random**, and more), and how you can configure the for various use cases.

By using Docker, we'll quickly spin up multiple backend services (which call "workers") and route requests through a single Caddy instance acting as our load balancer.

## The Project Setup

To get started, let's look at the project structure. Our setup is straightforward, allowing us to focus on the core concepts of load balancing.

Here's the project structure:

```sh
├── caddy
│   └── Caddyfile
├── docker-compose.yml
└── src
    ├── Dockerfile
    ├── go.mod
    └── main.go
```

Our setup is composes of three main parts:

**1.** **Backend Workers (`src`)**: These are simple Go applications the will handle the requests. Each worker will simply return a "Hello form [hostname]" message, allowing us to sess which server is handling the request. This is the perfect way to visualize how Caddy distributes the load.

**2.** **Caddy Load Balancer (`caddy`)**: Our Caddy instance will act as the reverse proxy, forwarding requets to the worker services. We'll use the `Caddyfile` to define our load balancing rules.

**3.** **Docker Compose (`docker.compose.yml`)**: This file orchestrates everything, defining and running our multi-container application with a single-command.

## Understading the Components

Let's break down the files in our project.

`src/main.go`

This is a simple Go HTTP server. It listens on port `8081` and responds to any request by printing its `hostname`. This is our primary tool for observing the load balancing behavior.

```go
package main

import (
	"fmt"
	"net/http"
	"os"
)

func handler(w http.ResponseWriter, r *http.Request) {
	hostname, _ := os.Hostname()
	fmt.Fprintf(w, "Hello from %s\n", hostname)
}

func main() {
	http.HandleFunc("/", handler)
	http.ListenAndServe(":8081", nil)
}
```

`src/Dockerfile`

This `Dockerfile` builds our Go application into a lightweight, self-contained Docker image.

```docker
FROM golang:1.24 AS builder

WORKDIR /go/src/app

COPY . .

RUN go mod download

RUN CGO_ENABLED=0 go build -o /go/bin/app

FROM golang:1.24-alpine

COPY --from=builder /go/bin/app /

EXPOSE 8081
ENV PORT 8081

CMD ["/app"]
```

`docker-compose.yml`

This file ties everything together. We define a service for our Caddy load balancer and three workers services.

```yml
version: "3.8"

services:
  load_balancer:
    image: caddy:2.10-alpine
    container_name: load_balancer
    ports:
      - "8082:80"
    volumes:
      - ./caddy/Caddyfile:/etc/caddy/Caddyfile

  worker_1:
    build: ./src
    container_name: worker_1
    hostname: worker_1
    expose:
      - "8081"

  worker_2:
    build: ./src
    container_name: worker_2
    hostname: worker_2
    expose:
      - "8081"

  worker_3:
    build: ./src
    container_name: worker_3
    hostname: worker_3
    expose:
      - "8081"
```

`caddy/Caddyfile`

This where the magic happends! The `Caddyfile` is Caddy's configuration file. We'll define a **reverse proxy** that routes to our workers. The `lb_policy` directive is where we'll specify our load balancing algorithms.

```go
:80 {
    reverse_proxy worker_1:8081  worker_2:8081  worker_3:8081 {
		lb_policy round_robin
	}
}
```

## Experimenting with Load Balancing Algorithms

Now that our project is set up, we can start experimenting. To run the project, simply execute docker-compose up in your terminal. You can then send requests to `http://127.0.0.1:8082` and observe which worker responds.

**1.** Round Robin (`lb_policy round_robin`)

**2.** Least Connection (`lb_policy least_conn`)

**3.** Random (`lb_policy random`)