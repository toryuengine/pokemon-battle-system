#include "choosecharacter.h"
#include <iostream>
#include <vector>
#include <conio.h>

std::vector<int> ChooseCharacter::select() {
    bool event = true;
    int position = 0;
    std::vector <int> chooselist; //選択リスト
    writeConsole(position, charalist);
    while (event){
        if (_kbhit()) { //キーボードが押下されたら
            int selectbtn = getCursor();
            if (selectbtn == 0 or selectbtn == 1) {//上下のボタン
                position = changePosition(position, selectbtn, charalist.size());
                writeConsole(position, charalist);
            }else if (selectbtn == 2){//space決定が押下されたときの処理
                chooselist.push_back(position);
                if(chooselist.size() == 3){//3体選択した時の処理
                    event = askToConfirm(chooselist);
                }
            }

        }
    }
    return chooselist;
};

//コンソールに表示
void ChooseCharacter::writeConsole(int select, std::vector <std::string> lists) {
    for (int i = 0; i < lists.size(); i++){
        if(select == i){
            std::cout << "▶" << lists[i] << std::endl;
        }else {
            std::cout << lists[i] << std::endl;
        }
    }
};


//選択中のカーソルの位置を出力する ue:0/shita:1/space:2
int ChooseCharacter::getCursor() {
    int select = 4;
    int ch = _getch();
    if (ch == 0xE0 || ch == 0x00) {
        int arrow = _getch();
        switch (arrow) {
            case 72://上キー
                select = 0;
                break;

            case 80: //下キー
                select = 1;
                break;

            default:
                break;
            }
    }else if (ch == 32){//space
        select = 2;
        std::cout << "space" << std::endl;
    }
    return select;
};

//ボタンに応じてポジションの位置を変更する
int ChooseCharacter::changePosition(int position, int selectbtn, int range) {
    if(selectbtn == 0){ //上ボタンが押されたときの処理
        position = position -1;
    }else if(selectbtn == 1){
        position = position + 1;
    }

    //ガードレール
    int newrange = range -1;
    if(position < 0){
        position = 0;
    }else if (position > newrange){
        position = newrange;
    }
    
    return position;  
};


//三体選択した時に、本当にこのポケモンでいいかの確認
bool ChooseCharacter::askToConfirm(std::vector <int> chooselist){
    

    for (int i = 0; i < chooselist.size(); i++){
        std::cout << charalist[chooselist[i]] << std::endl;
    }
    std::cout << "選択したこのポケモンでいいですか？" << std::endl;
    std::vector <std::string> yesno = {"はい", "いいえ"};

    int position = 0;
    bool event = true;//イベント
    while (event){
        if (_kbhit()){
            int selectbtn = getCursor();
            std::cout << "selectbtn" << selectbtn << std::endl;
            if (selectbtn == 0 or selectbtn == 1){
                std::cout << "ifを通った" << std::endl;
                position = changePosition(position, selectbtn, 1);
                writeConsole(position, yesno);
            }else if (selectbtn == 2) {
                if (position == 0){
                    event = false; 
                }else if (position == 1){
                    event = true;
                }
            }
        }
    }
    return false;
};



