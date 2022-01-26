package main

import (
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"net"
	"net/http"
	"os"

	"github.com/bitly/go-simplejson"
)

const aws_ip_uri = "https://ip-ranges.amazonaws.com/ip-ranges.json"

func main() {
	flag.Usage = func() {
		fmt.Fprintf(flag.CommandLine.Output(), "Usage: %s <ip>\n", os.Args[0])
		flag.PrintDefaults()
	}
	flag.Parse()
	if len(flag.Args()) != 1 {
		flag.Usage()
		check(errors.New("specify an IP address"), false)
	}
	ip := net.ParseIP(flag.Arg(0))
	if ip == nil {
		check(errors.New("bad IP address"), false)
	}
	resp, err := http.Get(aws_ip_uri)
	check(err, true)
	js, err := simplejson.NewFromReader(resp.Body)
	resp.Body.Close()
	check(err, true)
	out := make([]map[string]interface{}, 0, 20)
	for _, v := range js.Get("prefixes").MustArray() {
		va, ok := v.(map[string]interface{})
		if !ok {
			check(errors.New("invalid data"), false)
		}
		_, subnet, err := net.ParseCIDR(fmt.Sprint(va["ip_prefix"]))
		check(err, true)
		if subnet.Contains(ip) {
			out = append(out, va)
		}
	}
	data, err := json.MarshalIndent(out, "", "  ")
	check(err, true)
	fmt.Println(string(data))
}

func check(e error, doPanic bool) {
	if e != nil {
		if doPanic {
			panic(e.Error())
		} else {
			fmt.Println(e.Error())
			os.Exit(1)
		}
	}
}
