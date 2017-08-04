int port;
int value;
String temp;
int commaIndex;

void setup(){
  Serial.begin(9600);
}

void loop(){
  Serial.println("Ready");
  temp = readInfo();
  Serial.println(temp);
  commaIndex = temp.indexOf(',');
  port = (temp.substring(0,commaIndex)).toInt();
  value = (temp.substring(commaIndex + 1)).toInt();
  Serial.print("Setting port ");
  Serial.print(port);
  Serial.print(" to ");
  Serial.println(value);
  
  analogWrite(port, value);
 
}

String readInfo(){
  char c = ' ';
  String line = "";
  
  Serial.flush();
  while(c != '['){
    if (Serial.available() > 0)
      c = Serial.read();
  }
  while(c != ']') {
    if (Serial.available() > 0){
      line += c;
      c = Serial.read();
    }
  }
  
  return line.substring(1);
}
