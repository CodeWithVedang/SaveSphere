function toggleTheme() {
  const html = document.documentElement;
  const isDark = html.dataset.theme === 'dark';
  html.dataset.theme = isDark ? 'light' : 'dark';
}

function applyDefaultTheme() {
  // Set default theme without reading or saving to localStorage
  document.documentElement.dataset.theme = 'light';
}

async function loadRSS() {
  const container = document.getElementById('posts-container');
  const channelInfo = document.querySelector('.channel-info');
  const skeletonChannel = document.querySelector('.skeleton-channel');
  const channelTitle = document.getElementById('channel-title');
  const channelDesc = document.getElementById('channel-desc');
  const profileButton = document.getElementById('profile-button');

  try {
    const rssUrl = 'https://in.pinterest.com/Save_Sphere/feed.rss';
    const proxyUrl = 'https://api.allorigins.win/get?url=' + encodeURIComponent(rssUrl);
    const response = await fetch(proxyUrl);
    if (!response.ok) throw new Error('Network response was not ok');

    const data = await response.json();
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(data.contents, 'application/xml');

    const channel = xmlDoc.querySelector('channel');
    const title = channel.querySelector('title')?.textContent || 'Save Sphere';
    const description = channel.querySelector('description')?.textContent || 'Discover trending Amazon finds and deals!';
    const profileLink = channel.querySelector('link')?.textContent || 'https://www.pinterest.com/Save_Sphere/';

    channelTitle.textContent = title;
    channelDesc.textContent = description;
    profileButton.href = profileLink;
    skeletonChannel.style.display = 'none';
    channelInfo.style.display = 'block';

    const items = xmlDoc.querySelectorAll('item');
    container.innerHTML = '';

    items.forEach((item, index) => {
      const pinTitle = item.querySelector('title').textContent;
      const pinLink = item.querySelector('link').textContent;
      const description = item.querySelector('description').textContent;

      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = description;
      const img = tempDiv.querySelector('img');
      const imgSrc = img ? img.src : '';

      const postDiv = document.createElement('div');
      postDiv.className = 'post';
      postDiv.style.animationDelay = `${index * 0.1}s`;
      postDiv.innerHTML = `
        <a href="${pinLink}" target="_blank" rel="noopener noreferrer" class="post-link">
          ${imgSrc ? `<img src="${imgSrc}" alt="${pinTitle}" />` : ''}
          <div class="post-content">
            <div class="post-title">${pinTitle}</div>
            <a href="${pinLink}" target="_blank" rel="noopener noreferrer" class="pin-link" aria-label="View pin on Pinterest">View Pin</a>
          </div>
        </a>
      `;

      container.appendChild(postDiv);
    });
  } catch (error) {
    skeletonChannel.style.display = 'none';
    channelInfo.style.display = 'block';
    container.innerHTML = `<div class="loading">Failed to load pins. ${error.message}</div>`;
    console.error('Error loading RSS:', error);
  }
}

document.querySelector('.theme-toggle').addEventListener('click', toggleTheme);
applyDefaultTheme();
loadRSS();
