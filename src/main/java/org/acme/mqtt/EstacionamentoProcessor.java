package org.acme.mqtt;

import org.eclipse.microprofile.reactive.messaging.Incoming;
import org.eclipse.microprofile.reactive.messaging.Outgoing;

import io.smallrye.reactive.messaging.annotations.Broadcast;
import io.vertx.core.json.JsonObject;
import jakarta.enterprise.context.ApplicationScoped;

/**
 * Classe que processa os dados MQTT de vagas de estacionamento
 */
@ApplicationScoped
public class EstacionamentoProcessor {

    @Incoming("estacionamento/vagas")  // Nome do canal de entrada MQTT
    @Outgoing("vagas-stream")    // Nome do canal de saída
    @Broadcast
    public EstacionamentoData process(byte[] payload) {
        // Converte o payload para uma string
        String jsonStr = new String(payload);
        
        System.out.println("Recebendo dados do estacionamento: " + jsonStr);
        
        // Converte a string para um objeto JSON
        JsonObject json = new JsonObject(jsonStr);
        
        // Extrai o array de vagas
        int[] vagas = json.getJsonArray("vagas").stream()
                           .mapToInt(value -> ((Integer) value).intValue())
                           .toArray();
        
        // Cria e retorna o objeto com os dados processados
        EstacionamentoData estacionamentoData = new EstacionamentoData(vagas);
        
        System.out.println("Total de vagas: " + estacionamentoData.getTotalVagas() + 
                          ", Vagas livres: " + estacionamentoData.getVagasLivres() + 
                          ", Vagas ocupadas: " + estacionamentoData.getVagasOcupadas());
        
        return estacionamentoData;
    }
}
