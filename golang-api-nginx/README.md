# Deploying a Simple Go API with Supervisor and Nginx

## Intro

Hi! In this post, I'll show you how to deploy a simple Go API using Supervisor to manage the process and Nginx as a web server to serve it.

Before we dive into the deployment steps, let's briefly discuss why we're using Supervisor and Nginx.

- Supervisor is a process control system that helps manage and monitor applications running in the background. It ensures that your Go API stays up and automatically restarts it if it crashes. [See the full documentation](https://supervisord.org/introduction.html)

- Nginx is a high-performance web server that can also function as a reverse proxy, making it ideal for serving our Go API to the internet. [See the full documentation](https://nginx.org/en)

### 🤔 Why Choose Supervisor Over Other Options?

You might wonder why we use Supervisor instead of alternatives like [Systemd](https://systemd.io), [PM2](https://pm2.keymetrics.io), or containerized solutions like [Docker](https://www.docker.com/get-started). Here’s a quick comparison:

|Tools |Pros | Cons|
|---------|----------------------|-------|
| Supervisor | Simple setup, great for managing multiple processes, easy log management| Requires manual config|
| Systemd | Native to Linux, faster startup	| More complex setup, harder to debug |
| PM2 | Built for Node.js, supports process monitoring | Not ideal for Go applications |
| Docker | Isolated environment, easy deployment, scalable | More setup overhead, requires container knowledge |

#### When Should You Use Supervisor?

Use Supervisor when you want a simple, non-containerized way to manage a Go service, with features like auto-restart and log management, without dealing with systemd’s complexity or Docker’s extra overhead.

## Setup and Run a Simple Go API

### Requirements

Before starting, make sure you have golang installed on your system:

1. Go

	```bash
	$ go version

	go version go1.24.0 linux/amd64
	```

	If not installed, download it from [the official site](https://go.dev/dl).

2. Supervisor

- Ubuntu/Debian

	```bash
	$ sudo apt update
	$ sudo apt install supervisor -y
	```

- CentOS/RHEL

	```bash
	$ sudo yum install supervisor -y
	```

- Homebrew (macOS)

	```bash
	$ brew install supervisor
	```

	After installation, check if Supervisor is running:

	```bash
	$ sudo systemctl status supervisor
	```

	If it’s not running, start and enable it:

	```bash
	$ sudo systemctl start supervisor
	$ sudo systemctl enable supervisor
	```

3. Nginx

- Ubuntu/Debian

	```bash
	$ sudo apt install nginx -y
	```

- CentOS/RHEL

	```bash
	$ sudo yum install nginx -y
	```

- Homebrew (macOS)

	```bash
	$ brew install nginx
	```

	After installation, check if Nginx is running:

	```bash
	$ sudo systemctl status nginx
	```

	If it’s not running, start and enable it:

	```bash
	$ sudo systemctl start nginx
	$ sudo systemctl enable nginx
	```

### Initialize a New Go Project

First, create a new directory for the project and initialize a Go module:

```bash
$ cd /var/www/
$ mkdir go-api && cd go-api
```

```bash
$ go mod init example.com/go-api
```

This command creates a Go module named `example.com/go-api`, which helps manage dependencies.

#### Create a Simple API

Now, create a new file `main.go` and add the following code:

```bash
$ vim main.go
```

```go
package main

import (
        "fmt"
        "net/http"
)

func handler(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "text/plain")
        fmt.Fprintln(w, "Simple Go API")
}

func main() {
        http.HandleFunc("/", handler)
        fmt.Println("Server started at :8080")
        http.ListenAndServe(":8080", nil)
}
```

Compile and run the Go server:

```bash
$ go run main.go
```

If successful, you should see this message in the terminal:

```bash
Server started at :8080
```

Now test the API using `curl`:

```bash
$ curl localhost:8080


Simple Go API
```

#### Create a Simple API with ASCII Text Response (Optional)

First, install the go-figure package:

```bash
$ go get github.com/common-nighthawk/go-figure
```

Now, modify `main.go` to generate an ASCII text response dynamically:

```go
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
```

```bash
$ curl localhost:8080

  ____    _                       _             ____                _      ____    ___
 / ___|  (_)  _ __ ___    _ __   | |   ___     / ___|   ___        / \    |  _ \  |_ _|
 \___ \  | | | '_ ` _ \  | '_ \  | |  / _ \   | |  _   / _ \      / _ \   | |_) |  | |
  ___) | | | | | | | | | | |_) | | | |  __/   | |_| | | (_) |    / ___ \  |  __/   | |
 |____/  |_| |_| |_| |_| | .__/  |_|  \___|    \____|  \___/    /_/   \_\ |_|     |___|
                         |_|
```

### Running the API as a Background Service with Supervisor

#### Create a Supervisor Configuration for the Go API

Create a new Supervisor config file:

```bash
$ sudo vim /etc/supervisor/conf.d/go-api.conf
```

Add the following configuration:

```bash
[program:go-api]
process_name=%(program_name)s_%(process_num)02d
directory=/var/www/go-api
command=bash -c 'cd /var/www/go-api && ./main'
autostart=true
autorestart=true
user=www-data
redirect_stderr=true
stderr_logfile=/var/log/go-api.err.log
stdout_logfile=/var/log/go-api.out.log
```

Now, we need build the Go API:

```bash
go build -o main .
```

Ensure the directory and binary have the correct permissions:

```bash
sudo chown -R www-data:www-data /var/www/go-api
sudo chmod 775 /var/www/go-api/main
```

#### Apply the Supervisor Configuration

Reload Supervisor and start the service:

```bash
$ sudo supervisorctl reread
$ sudo supervisorctl update
$ sudo supervisorctl start go-api:*
```

Check the service status:

```bash
$ sudo supervisorctl avail
go-api:go-api_00                 in use    auto      999:999
```

```bash
$ sudo supervisorctl status go-api:*

go-api:go-api_00                 RUNNING   pid 198867, uptime 0:01:52
```

#### Check Logs and Debugging

If the API is not running, check the logs:

```bash
cat /var/log/go-api.out.log
cat /var/log/go-api.err.log
```

Or use Supervisor’s built-in log viewer:

```bash
$ sudo supervisorctl tail -f go-api:go-api_00

==> Press Ctrl-C to exit <==
Server started at :8080
```

### Setting Up Nginx as a Reverse Proxy for the API

#### Create a new configuration file:

```bash
$ sudo vim /etc/nginx/sites-available/go-api
```

```sh
server {
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }

    error_log /var/log/nginx/go-api_error.log;
    access_log /var/log/nginx/go-api_access.log;
}
```

Create a symbolic link to enable the site:

```bash
$ sudo ln -s /etc/nginx/sites-available/go-api /etc/nginx/sites-enabled/
```

Test the configuration:

```bash
$ nginx -t

nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

If the test is successful, restart Nginx:

```bash
$ sudo systemctl restart nginx
```

Now, you can access your Go API using:

- Localhost (if running locally)

```bash
curl http://localhost

  ____    _                       _             ____                _      ____    ___
 / ___|  (_)  _ __ ___    _ __   | |   ___     / ___|   ___        / \    |  _ \  |_ _|
 \___ \  | | | '_ ` _ \  | '_ \  | |  / _ \   | |  _   / _ \      / _ \   | |_) |  | |
  ___) | | | | | | | | | | |_) | | | |  __/   | |_| | | (_) |    / ___ \  |  __/   | |
 |____/  |_| |_| |_| |_| | .__/  |_|  \___|    \____|  \___/    /_/   \_\ |_|     |___|
                         |_|
```

- Server’s Public IP (if running on a VPS or remote server)

```bash
curl http://YOUR_SERVER_IP
```

> Note: If you want to access your Go API using a custom domain instead of an IP address, you need to purchase a domain, configure its DNS to point to your server’s IP, and update your Nginx configuration accordingly. For better security, it's recommended to set up HTTPS using Let's Encrypt.

### Conslusion

In this guide, we deployed a simple Go API using Supervisor to manage the process and Nginx as a reverse proxy, ensuring automatic restarts and efficient request handling. Thank you for reading, and good luck with your deployment! 🚀
