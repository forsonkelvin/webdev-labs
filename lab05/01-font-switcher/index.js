let currentFontSize = 1.4;

const makeBigger = () => {
  currentFontSize += 0.2;
  updateFontSize()
};

const makeSmaller = () => {
  currentFontSize -= 0.2;
  updateFontSize()
};

const updateFontSize = () =>{
  document.querySelector(".content").style.fontSize = `${currentFontSize}em`;
  document.querySelector("h1").style.fontSize = `${currentFontSize + 1}em`;
}


document.querySelector("#a1").addEventListener('click', makeBigger);
document.querySelector("#a2").addEventListener('click', makeSmaller);
