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