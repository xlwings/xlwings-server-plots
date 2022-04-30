// TODO: Replace URL with your own URL
const base_url = "URL";
const token = ScriptApp.getOAuthToken();

function pandas() {
  runPython(base_url + "/timeseries/random-walk", { apiKey: token });
}
