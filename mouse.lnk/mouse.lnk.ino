#include <Mouse.h>
#include <Keyboard.h>

String serialString;

void setup()
{
   Serial.begin(9600);
   Mouse.begin();
   Keyboard.begin();
}

void mouseMove(String serialString, bool reverse)
{
  String pixel = serialString.substring(4);
  int delimiter = pixel.lastIndexOf(':');
  int x = pixel.substring(0, delimiter).toInt();
  int y = pixel.substring(delimiter+1).toInt();

  int mx = 0;
  int my = 0;
  int xMoveDir = 1;
  int yMoveDir = 1;

  if (reverse) {
    x = -x;
    y = -y;  
  }

  if (x < 0) {
    xMoveDir = -1;
  }
  if (y < 0) {
    yMoveDir = -1;  
  }
  x = abs(x);
  y = abs(y);
  while (mx < x && my < y) {
    Mouse.move(xMoveDir,yMoveDir,0);
    mx++;
    my++;
  }
  while (mx < x) {
    Mouse.move(xMoveDir,0,0);
    mx++;
  }
  while (my < y) {
    Mouse.move(0,yMoveDir,0);
    my++;
  }
}

void mouseClick(char bt)
{
  Mouse.press(bt);
  delay(50);
  Mouse.release(bt);
}

void keyPress(char key)
{
  if (key == '*') {
    Keyboard.press(KEY_RETURN);
  } else {
    Keyboard.press(key);
  }
  delay(50);
  Keyboard.releaseAll();
}

void switchWindow()
{
  Keyboard.press(KEY_LEFT_ALT);
  Keyboard.press(KEY_TAB);
  Keyboard.releaseAll();
}

void initBattle(String serialString)
{
  mouseMove(serialString, false);
  delay(300);
  keyPress('5');
  delay(100);
  keyPress('g');
  delay(100);
  mouseClick(MOUSE_LEFT);
  delay(500);
//  keyPress('8');
//  delay(100);
//  keyPress('g');
//  delay(100);
//  mouseClick(MOUSE_LEFT);
//  delay(500);
//  keyPress('7');
//  delay(100);
//  mouseClick(MOUSE_RIGHT);
  delay(500);
  keyPress('4');
  delay(100);
  keyPress('r');
  delay(100);
  mouseClick(MOUSE_LEFT);
  delay(1000);
  keyPress('3');
  delay(100);
  keyPress('r');
  delay(100);
  mouseClick(MOUSE_LEFT);
  delay(500);
  keyPress('0');
  delay(100);
  keyPress('h');
  delay(100);
  mouseMove(serialString, true);
}

void eatFood(String serialString)
{
  delay(50);
  keyPress('f');
  delay(50);
  keyPress(serialString.charAt(2));
  delay(50);
  keyPress('i');
  mouseMove(serialString, false);
  delay(100);
  mouseClick(MOUSE_RIGHT);
  delay(100);
  mouseMove(serialString, true);
  delay(100);
  keyPress('i');
  delay(50);
  keyPress('f');
}

void loop()
{
  if (Serial.available() > 0) {
    // read the incoming byte:
    serialString = Serial.readStringUntil('\n');
    if (serialString.charAt(0) == 'm') {
    // m:r:100:100
      if (serialString.charAt(2) == 'r') {
        mouseMove(serialString, false);
        mouseClick(MOUSE_RIGHT);
        mouseMove(serialString, true);
      } else if (serialString.charAt(2) == 'l') {
        mouseMove(serialString, false);
        delay(100);
        mouseClick(MOUSE_LEFT);
        delay(100);
        mouseMove(serialString, true);
      } else if (serialString.charAt(2) == 'f') {
        mouseMove(serialString, false);
      } else if (serialString.charAt(2) == 'b') {
        mouseMove(serialString, true);
      }
    } else if (serialString.charAt(0) == 'k') {
      keyPress(serialString.charAt(2));
    } else if (serialString.charAt(0) == 'b') {
      initBattle(serialString);
    } else if (serialString.charAt(0) == 's') {
      eatFood(serialString);
    } else if (serialString.charAt(0) == 'p') {
      switchWindow();
    }
  }
}

