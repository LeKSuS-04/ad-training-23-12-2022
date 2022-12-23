FROM golang:1.19 as build

EXPOSE 8080

WORKDIR /go/src/app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 go build -o /go/bin/gingerbreach


FROM gcr.io/distroless/static-debian11

COPY --from=build /go/bin/gingerbreach /
CMD ["/gingerbreach"]
