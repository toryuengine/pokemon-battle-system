#include <iostream>
#include <cstdlib> // std::system のために必要

struct status {
    int hp;
    int attack;
};

int main() {
    int i = 1;
    status Typhlosion = {220, 15}; //ラグラージ
    status Swampert = {204, 22};//バクフーン
    std::system("chcp 65001"); // コンソールをUTF-8モードに変更
    bool battle = true;

    while (battle) {
        std::cout << "ターン" << i << std::endl;

        // if-else文を使うことで、条件分岐を1回にまとめる
        // if (i % 2 != 0) {
            
        Swampert.hp = Swampert.hp - Typhlosion.attack;
        std::cout << "ラグラージの残りＨＰ" << Swampert.hp << std::endl;

        // } else {
        Typhlosion.hp = Typhlosion.hp - Swampert.attack;
        std::cout << "バクフーンの残りＨＰ" << Typhlosion.hp << std::endl;
        // }

        std::cin.get(); 
        i++;

    //戦闘終了
        if(Typhlosion.hp <= 0) {
            battle = false;
        }else if (Swampert.hp <= 0) {
            battle = false;
        }
    }
    std::cout << "戦闘終了" << std::endl;
    return 0; // 無限ループのため実際には到達しません
}
