const zhuyinAnswer = document.querySelector("#zhuyin-answer");
const zhuyinKeys = document.querySelectorAll(
  ".zhuyin-keyboard [data-symbol]"
);

zhuyinKeys.forEach((key) => {
  key.addEventListener("click", () => {
    zhuyinAnswer.value += key.dataset.symbol;
  });
});

document
  .querySelector("#zhuyin-backspace")
  .addEventListener("click", () => {
    zhuyinAnswer.value = zhuyinAnswer.value.slice(0, -1);
  });

document
  .querySelector("#zhuyin-clear")
  .addEventListener("click", () => {
    zhuyinAnswer.value = "";
  });