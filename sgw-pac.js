function FindProxyForURL(url, host) {
  const PROXY = "HTTPS ingress.cloudproxy.app:443";
  const sites = ["ipify.org", "onprem.securebrowsing.cloud"]; // add URLs to match all of your SWG app domains

  for (const site of sites) {
    if (shExpMatch(url, 'https://' + site + '/*') || shExpMatch(url, '*.' + site + '/*')) {
      return PROXY;
    }
  }
  return 'DIRECT';
}
