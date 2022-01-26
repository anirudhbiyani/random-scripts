#!/usr/bin/env ruby

# Query the AWS IP range list, filter for the given IP/subnet, and spit
# the results back as JSON

require 'json'
require 'net/http'
require 'ipaddr'

AWS_IP_URI = URI('https://ip-ranges.amazonaws.com/ip-ranges.json')

req_ip = IPAddr.new(ARGV.shift) rescue abort("Usage: #{$0} ip[/prefix]")

aws_ips = nil

Net::HTTP.start(AWS_IP_URI.host, AWS_IP_URI.port,
  :use_ssl => AWS_IP_URI.scheme == 'https') do |http|
  request = Net::HTTP::Get.new AWS_IP_URI
  response = http.request request # Net::HTTPResponse object
  aws_ips = JSON.parse(response.body)
end

filtered = []

aws_ips['prefixes'].each do |pfx|
  pfx_ip = IPAddr.new(pfx['ip_prefix'])
  filtered << pfx if pfx_ip.include?(req_ip)
end

puts JSON.pretty_generate(filtered)
