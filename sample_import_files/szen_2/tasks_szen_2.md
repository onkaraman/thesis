Onur Karaman, BA 2019
### Aufgabenliste um Szenario 2 zu realisieren
-------------------------------------------

<b>1</b>:  Einzelne Teilquellen (TQ) in das Fusionstool (FT) laden.

<b>2</b>: Pro TQ die Spalten `Platform`, `Downloads`, `Unique downloads` und `Interaction (min/day)` der Teilfusion (TF) hinzufügen.

<b>3</b>: Die TF so formatieren, dass Werte unter den gleichen Spaltennamen zusammengefasst werden.

<b>4</b>: Spalte `%-Anteil DL` erstellen mit Spaltenregel: 
WENN `platform` CONTAINS `*`, DANN Neue Spalte: `%-Anteil DL` mit APPLY `-`

<b>5</b>: `%-Anteil` mit Skriptregel berechnen und eintragen: 

``share = (float(_row["DOW"]) * 100)/_row["DOW.SUM"]``
``_row["% A"] = round(share)``

<b>6</b>: (Optional): `Summe DL`-Regel löschen
