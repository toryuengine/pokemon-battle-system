#include "choosecharacter.h"
#include <iostream>
#include <vector>
int main(){
    system("chcp 65001");
    ChooseCharacter choosecharacter;
    std::vector <int> charas = choosecharacter.select();
};