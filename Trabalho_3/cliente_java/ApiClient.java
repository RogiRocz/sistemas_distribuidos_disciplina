import com.google.gson.*;
import java.net.http.*;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class ApiClient {
    private static final String API_URL = "http://127.0.0.1:8000";
    private final HttpClient httpClient;
    private final Gson gson;
    private String ultimaResposta = "";

    public ApiClient() {
        this.httpClient = HttpClient.newHttpClient();
        this.gson = new GsonBuilder().setPrettyPrinting().create();
    }

    // GET Request
    public JsonElement get(String endpoint) {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(API_URL + endpoint))
                    .GET()
                    .header("Content-Type", "application/json")
                    .build();

            HttpResponse<String> response = httpClient.send(request, 
                    HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));

            ultimaResposta = String.format("[%s] GET %s -> %d", 
                    getTimestamp(), endpoint, response.statusCode());
            
            if (response.statusCode() == 200) {
                return JsonParser.parseString(response.body());
            }
            return null;
        } catch (Exception e) {
            ultimaResposta = "[" + getTimestamp() + "] ❌ Erro de Conexão!";
            System.err.println("Erro na requisição GET: " + e.getMessage());
            return null;
        }
    }

    // POST Request
    public JsonElement post(String endpoint, JsonObject body) {
        try {
            String jsonBody = gson.toJson(body);
            
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(API_URL + endpoint))
                    .POST(HttpRequest.BodyPublishers.ofString(jsonBody, StandardCharsets.UTF_8))
                    .header("Content-Type", "application/json")
                    .build();

            HttpResponse<String> response = httpClient.send(request, 
                    HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));

            ultimaResposta = String.format("[%s] POST %s -> %d", 
                    getTimestamp(), endpoint, response.statusCode());
            
            if (response.statusCode() == 200 && !response.body().isEmpty()) {
                return JsonParser.parseString(response.body());
            }
            return null;
        } catch (Exception e) {
            ultimaResposta = "[" + getTimestamp() + "] ❌ Erro de Conexão!";
            System.err.println("Erro na requisição POST: " + e.getMessage());
            return null;
        }
    }

    public String getUltimaResposta() {
        return ultimaResposta;
    }

    private String getTimestamp() {
        Calendar cal = Calendar.getInstance();
        return String.format("%02d:%02d:%02d", 
                cal.get(Calendar.HOUR_OF_DAY),
                cal.get(Calendar.MINUTE),
                cal.get(Calendar.SECOND));
    }

    public void imprimirJson(JsonElement json) {
        if (json != null) {
            System.out.println(gson.toJson(json));
        }
    }
}
