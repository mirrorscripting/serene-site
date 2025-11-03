import { getMoonPhase, nextFullMoon } from '../lib/moon.js';

function formatDate(date) {
  return new Intl.DateTimeFormat('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  }).format(date);
}

function formatIllumination(value) {
  return `${Math.round(value * 100)}% illuminated`;
}

export default function LunarWidget() {
  let activeDate = new Date();

  const container = document.createElement('section');
  container.className = 'lunar-widget';

  const header = document.createElement('header');
  const title = document.createElement('h2');
  title.textContent = 'Lunar Phase';
  header.appendChild(title);

  const dateText = document.createElement('p');
  dateText.className = 'lunar-date';
  header.appendChild(dateText);

  const body = document.createElement('div');
  body.className = 'lunar-body';

  const emoji = document.createElement('div');
  emoji.className = 'lunar-emoji';
  body.appendChild(emoji);

  const phaseText = document.createElement('p');
  phaseText.className = 'lunar-phase';
  body.appendChild(phaseText);

  const illuminationText = document.createElement('p');
  illuminationText.className = 'lunar-illumination';
  body.appendChild(illuminationText);

  const nextFullMoonText = document.createElement('p');
  nextFullMoonText.className = 'lunar-next-full';
  body.appendChild(nextFullMoonText);

  const controls = document.createElement('div');
  controls.className = 'lunar-controls';

  const prevButton = document.createElement('button');
  prevButton.type = 'button';
  prevButton.textContent = 'Previous Day';
  prevButton.addEventListener('click', () => {
    activeDate = new Date(activeDate.getTime() - 24 * 60 * 60 * 1000);
    render();
  });

  const nextButton = document.createElement('button');
  nextButton.type = 'button';
  nextButton.textContent = 'Next Day';
  nextButton.addEventListener('click', () => {
    activeDate = new Date(activeDate.getTime() + 24 * 60 * 60 * 1000);
    render();
  });

  controls.appendChild(prevButton);
  controls.appendChild(nextButton);

  container.appendChild(header);
  container.appendChild(body);
  container.appendChild(controls);

  function render() {
    const phase = getMoonPhase(activeDate);
    const upcomingFull = nextFullMoon(activeDate);

    dateText.textContent = formatDate(activeDate);
    emoji.textContent = phase.emoji;
    phaseText.textContent = phase.name;
    illuminationText.textContent = formatIllumination(phase.illumination);
    nextFullMoonText.textContent = `Next full moon: ${formatDate(upcomingFull)}`;
  }

  render();

  return container;
}
