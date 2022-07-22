const byte counterPin = 3;
volatile int counterPulses = 0;

void setup() {
  pinMode(counterPin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(counterPin), counterevent, FALLING);
  Serial.begin(9600);
}

void loop() {
  String cmd;
  while (Serial.available() > 0) {
    cmd = Serial.readString();
    if (cmd == "G") {
      outputcounts();
    }
    else if (cmd == "F") {
      flushCount();
      Serial.println("flushed");
    }
    else {
      Serial.println("unknown command");
      cmd = "";
    }
  }
}

void counterevent() {
  counterPulses++;
}

void outputcounts() {
  char context[220];
  sprintf(context, "Counts: %d", counterPulses);
  Serial.println(context);
}

void flushCount() {
  counterPulses = 0;
}

