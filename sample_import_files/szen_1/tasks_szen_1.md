Onur Karaman, BA 2019
### Aufgabenliste um Szenario 1 zu realisieren
-------------------------------------------

<b>1</b>: Einzelne Teilquellen (TQ) in das Fusionstool (FT) laden.

<b>2</b>: Alle Inhalte/Spalten der TQs zusammenführen (in die TF einfügen).

<b>3</b>: Die TF so formatieren, dass Werte unter den gleichen Spaltennamen zusammengefasst werden.

<b>4</b>: Dynamische Fehlercodes generieren: 
1. Wenn (`tool_x_code` = `DJ10+1e`) UND (`cad_valide` = `0`), dann neue Spalte "Fehlercode" = FFT
2. Wenn (`cad_valide` = `1`) UND (`cac_valide` = `0`), dann Spalte "Fehlercode" = CAF
3. Wenn (`cad_valide` = 0) UND (`cac_valide` = 1), dann Spalte "Fehlercode" = CAG
4. Wenn (`bauteilcode` CONTAINS 2x den gleichen Buchstaben), dann Spalte "Fehlercode" = DUPLO
``if len(_row["BAUE"]) > len(set(_row["BAUE"])): _row["FEH"] = "DUPLO"``
5. Wenn (`bauteilversion` > 5), dann `bauteilcode` mit Präfix "2012: "
``if float(_row["BAUN"]) > 5: _row["BAUE"] = "2012: %s" % _row["BAUE"]``

<b>5</b>: Teilfusion als Endfusion herunterladen