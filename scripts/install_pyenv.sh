path=""
name=""

while getopts 'p:n:' flag;
do
    case "$flag" in
        p) path=${OPTARG};;
        n) name=${OPTARG};;
    esac
done

if [[ $name == "" ]]
then
	echo "Name parameter is mandatory"
	exit 2
fi
if [[ $path == "" ]]
then
	echo "Path parameter is mandatory"
	exit 2
fi

current_path=$(pwd);

#Set current directory

echo "Building python environment"
cd $path;

pyenv virtualenv --force 3.9.6 "pyenv.$name";
pyenv local pyenv.$name;
pip install --upgrade pip setuptools;
pip install -r requirements.txt;

cd $current_path;