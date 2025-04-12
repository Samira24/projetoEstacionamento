package org.acme.mqtt;

public class EstacionamentoData {
    private int[] vagas;
    private int vagasLivres;
    private int vagasOcupadas;

    public EstacionamentoData(int[] vagas) {
        this.vagas = vagas;
        this.vagasLivres = 0;
        this.vagasOcupadas = 0;

        for (int status : vagas) {
            if (status == 0) vagasLivres++;
            else vagasOcupadas++;
        }
    }

    public int[] getVagas() {
        return vagas;
    }

    public int getVagasLivres() {
        return vagasLivres;
    }

    public int getVagasOcupadas() {
        return vagasOcupadas;
    }

    public int getTotalVagas() {
        return vagas.length;
    }
}
