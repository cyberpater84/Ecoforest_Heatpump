# Ecoforest Heat Pump — Home Assistant integratie

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![HA version](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-blue)](https://www.home-assistant.io/)

Volledige Home Assistant integratie voor Ecoforest **ecoAIR** warmtepompen via **Modbus TCP**.  
Communiceert direct met de BMS2-poort van de warmtepomp via een goedkope RS485-naar-TCP converter (bijv. Waveshare, AliExpress).

---

## Functies

- **Sensoren** — alle temperaturen, drukken, vermogens, COP/EER/SPF, compressorsnelheid
- **Binaire sensoren** — pompstatus, ventielen, boiler/zwembad actief, alarmstatus
- **Schakelaar** — warmtepomp aan/uit via BUS (coil 180)
- **Getal-entiteiten** — alle BUS-setpoints (boiler, SG1/SG2/SG3 verwarming en koeling, zwembad) + demands en programma
- **Maandelijkse energietellers** — verwarming, koeling en elektra per maand
- Poll-interval instelbaar via de opties (10–300 seconden)
- Volledige HACS-ondersteuning via Config Flow UI
- Nederlandse én Engelse UI

---

## Vereisten

### Hardware
- Ecoforest ecoAIR warmtepomp (1-7, 1-9, 3-12 of 4-20 kW)
- RS485-naar-TCP converter aangesloten op de **BMS2**-poort van de warmtepomp  
  (bijv. Waveshare RS485 to ETH, of vergelijkbaar AliExpress model)
- Vaste IP op de converter (DHCP-reservering aanbevolen)

### Warmtepomp instellen
1. Ga in het installateursinstelling naar **Configuration → Remote Control → BMS remote control**
2. Activeer de **BMS remote control** checkbox (vereist voor schrijven van setpoints en aan/uit)
3. Configureer de BMS2-poort:
   - Baudrate: **19200**
   - Stop bits: **2**
   - Parity: **None**
   - Slave-adres: kies zelf (standaard 1)
   - Protocol: **MB Slave** of **MB SLV. EXT**

> Als u alleen wilt uitlezen (geen schrijven) hoeft de BMS remote control **niet** geactiveerd te zijn.

---

## Installatie via HACS

1. Ga in HACS naar **Integraties → Aangepaste repositories**
2. Voeg toe: `https://github.com/cyberpater84/ecoforest-hacs` (categorie: Integratie)
3. Installeer **Ecoforest Heat Pump**
4. Herstart Home Assistant
5. Ga naar **Instellingen → Apparaten & Diensten → Integratie toevoegen**
6. Zoek op **Ecoforest**
7. Vul in: IP-adres van de converter, poort (standaard 502), slave-adres

---

## Handmatige installatie

```
custom_components/ecoforest/  →  kopieer naar <HA config>/custom_components/ecoforest/
```

Herstart HA, daarna via UI instellen zoals hierboven.

---

## Entiteiten overzicht

### Sensoren (read-only)
| Naam | Register | Eenheid |
|------|----------|---------|
| Aanvoertemperatuur binnenunit | HR 1 | °C |
| Retourtemperatuur binnenunit | HR 2 | °C |
| Buitentemperatuur | HR 20 | °C |
| Buffervattemperatuur verwarming | HR 17 | °C |
| Boilertemperatuur | HR 11 | °C |
| Condensatietemperatuur | HR 25 | °C |
| Verdampingstemperatuur | HR 27 | °C |
| COP verwarming | HR 136 | — |
| EER koeling | HR 137 | — |
| Actueel verwarmingsvermogen | HR 133 | kW |
| Actueel elektrisch vermogen | HR 135 | kW |
| Compressorsnelheid | HR 5002 | rpm |
| SPF jaarlijks | HR 227 | — |
| Maandelijkse verwarming jan-dec | HR 5233-5244 | kWh |
| Maandelijkse elektra jan-dec | HR 5245-5256 | kWh |
| *(en veel meer…)* | | |

### Schakelaar
| Naam | Coil | Omschrijving |
|------|------|--------------|
| Warmtepomp aan/uit via BUS | 180 | Schakelt de pomp in/uit via BMS |

### Getal-entiteiten (schrijfbaar)
| Naam | Register | Bereik |
|------|----------|--------|
| BUS Boiler setpoint | HR 168 | 0–70 °C |
| BUS Verwarmingssetpoint SG1 | HR 170 | 0–60 °C |
| BUS Verwarmingssetpoint SG2 | HR 171 | 0–60 °C |
| BUS Verwarmingssetpoint SG3 | HR 172 | 0–60 °C |
| BUS Koelsetpoint SG1 | HR 175 | 0–25 °C |
| BUS Vraag SG1 | HR 5183 | 0=geen, 1=verwarmen, 2=koelen |
| BUS Programma | HR 5188 | 0=geen, 1=winter, 2=zomer |
| *(en meer…)* | | |

---

## Bekende beperkingen

- Alleen **ecoAIR** domestic (1-22 kW). ecoGEO en high-power (12-100 kW) komen in een latere versie.
- Modbus RTU (serieel) wordt niet ondersteund — alleen TCP.
- De BMS-poort ondersteunt maar één master tegelijk. Als je ook een Easynet-module of th-tune hebt die de BMS2-poort gebruikt, heb je een uitbreidingskaart nodig voor een tweede BMS-poort.

---

## Bijdragen

Pull requests welkom. Open eerst een issue voor grotere wijzigingen.  
Voor de ecoGEO of high-power registermap: zie het officiële Ecoforest Modbus Guide PDF.

---

## Licentie

MIT
