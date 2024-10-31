from django.shortcuts import render
from django.http import HttpResponse

from .tasks import generate_usn_list, scrape_data, process_and_save_data, initialize_webdriver, download_excel

from .forms import UserInput



def scraper(request):
    if request.method == 'POST':
        form = UserInput(request.POST)
        if form.is_valid():
            usn = form.cleaned_data['prefix_usn'].upper()
            usn_range = form.cleaned_data['usn_range']
            sem = form.cleaned_data['sem']
            url = form.cleaned_data['url']

            is_reval = 'RV' in url
            usn_list = generate_usn_list(usn, usn_range)

            driver = initialize_webdriver(url)
            soup_dict = scrape_data(driver, usn_list)
            driver.quit()

            if soup_dict:
                df = process_and_save_data(soup_dict, is_reval)
                response = download_excel(df, sem)
                return response
    else:
        form = UserInput()

    return render(request, 'scraper.html', {'form': form})
