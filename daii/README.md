Eu prefiro fazer as coisas no meu pc, já tenho docker aqui e tudo. 

O que eu fiz foi criar uma pasta .docker (coloquei no .gitignore pra não jogar as imagens gigantes pro repo) e puxar as coisas pra lá. 

(Tem que baixar o docker desktop antes)


No prompt de comando com permissão de admin: 
```
cd daii
mkdir .docker
cd .docker
git clone https://github.com/fabiogjardim/bigdata_docker.git
cd bigdata_docker 
docker-compose up -d
```