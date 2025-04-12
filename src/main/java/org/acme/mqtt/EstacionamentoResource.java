package org.acme.mqtt;

import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

import org.eclipse.microprofile.reactive.messaging.Channel;
import io.smallrye.mutiny.Multi;

@Path("/estacionamento")
public class EstacionamentoResource {

    @Inject
    @Channel("vagas-stream")
    Multi<EstacionamentoData> vagasStream;

    private volatile EstacionamentoData ultimo;

    @GET
    @Produces(MediaType.TEXT_PLAIN)
    public String hello() {
        return "Serviço de monitoramento de estacionamento";
    }

    // SSE emitindo objetos EstacionamentoData como JSON
    @GET
    @Path("/stream")
    @Produces(MediaType.SERVER_SENT_EVENTS)
    public Multi<String> stream() {
        return vagasStream
            .invoke(data -> this.ultimo = data)
            .map(this::toJson);
    }

    @GET
    @Path("/status")
    @Produces(MediaType.APPLICATION_JSON)
    public Response status() {
        if (ultimo == null) return Response.noContent().build();

        double ocupacao = (ultimo.getVagasOcupadas() * 100.0) / ultimo.getTotalVagas();
        String json = String.format(
            "{ \"totalVagas\": %d, \"vagasLivres\": %d, \"vagasOcupadas\": %d, \"ocupacao\": \"%.2f%%\" }",
            ultimo.getTotalVagas(),
            ultimo.getVagasLivres(),
            ultimo.getVagasOcupadas(),
            ocupacao
        );
        return Response.ok(json).build();
    }

    @GET
    @Path("/detalhes")
    @Produces(MediaType.APPLICATION_JSON)
    public Response detalhes() {
        if (ultimo == null) return Response.noContent().build();

        StringBuilder json = new StringBuilder();
        json.append("{");
        json.append("\"totalVagas\": ").append(ultimo.getTotalVagas()).append(", ");
        json.append("\"vagasLivres\": ").append(ultimo.getVagasLivres()).append(", ");
        json.append("\"vagasOcupadas\": ").append(ultimo.getVagasOcupadas()).append(", ");
        json.append("\"detalhes\": [");

        int[] vagas = ultimo.getVagas();
        for (int i = 0; i < vagas.length; i++) {
            if (i > 0) json.append(", ");
            json.append("{");
            json.append("\"vaga\": ").append(i).append(", ");
            json.append("\"status\": \"").append(vagas[i] == 0 ? "livre" : "ocupada").append("\"");
            json.append("}");
        }

        json.append("]}");
        return Response.ok(json.toString()).build();
    }

    private String toJson(EstacionamentoData data) {
        StringBuilder json = new StringBuilder();
        json.append("{");
        json.append("\"totalVagas\": ").append(data.getTotalVagas()).append(", ");
        json.append("\"vagasLivres\": ").append(data.getVagasLivres()).append(", ");
        json.append("\"vagasOcupadas\": ").append(data.getVagasOcupadas()).append(", ");
        json.append("\"detalhes\": [");

        int[] vagas = data.getVagas();
        for (int i = 0; i < vagas.length; i++) {
            if (i > 0) json.append(", ");
            json.append("{");
            json.append("\"vaga\": ").append(i).append(", ");
            json.append("\"status\": \"").append(vagas[i] == 0 ? "livre" : "ocupada").append("\"");
            json.append("}");
        }

        json.append("]}");
        return json.toString();
    }
}
