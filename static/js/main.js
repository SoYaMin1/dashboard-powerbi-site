document.addEventListener("DOMContentLoaded", () => {
  // Power BI: скрываем спиннер, когда iframe загрузился
  document.querySelectorAll(".pbi-wrapper iframe").forEach((frame) => {
    const wrapper = frame.closest(".pbi-wrapper");
    const markLoaded = () => wrapper.classList.add("is-loaded");
    frame.addEventListener("load", markLoaded);
    setTimeout(markLoaded, 20000); // запасной вариант, если событие load не пришло
  });

  // Кнопка «На весь экран» (Fullscreen API)
  const fullscreenSupported = document.fullscreenEnabled || document.webkitFullscreenEnabled;
  document.querySelectorAll("[data-fullscreen-target]").forEach((button) => {
    const target = document.querySelector(button.dataset.fullscreenTarget);
    if (!target || !fullscreenSupported) {
      button.hidden = true;
      return;
    }
    button.addEventListener("click", () => {
      if (document.fullscreenElement || document.webkitFullscreenElement) {
        (document.exitFullscreen || document.webkitExitFullscreen).call(document);
      } else {
        (target.requestFullscreen || target.webkitRequestFullscreen).call(target);
      }
    });
  });

  // Автоматически скрываем flash-сообщения об успехе через 6 секунд
  document.querySelectorAll(".alert-success.alert-dismissible").forEach((el) => {
    setTimeout(() => {
      if (window.bootstrap) bootstrap.Alert.getOrCreateInstance(el).close();
    }, 6000);
  });
});