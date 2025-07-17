function FindProxyForURL(url, host) {
  const PROXY = "HTTPS ingress.cloudproxy.app:443";

  const sites = [${sites_list}];

  for (const site of sites) {
    if (shExpMatch(url, 'https://' + site + '/*') || shExpMatch(url, '*.' + site + '/*')) {
      return PROXY;
    }
  }
  return 'DIRECT';
}
