const BASE_URL = "https://melomap.onrender.com/";


// axios request to view bookmarked songs without reload
async function displayBookmarkedSongs(evt){
    let $target = $(evt.target)
    const userId = $target.data("userid")
    // send request
    const htmlResp = await axios.get(`${BASE_URL}users/${userId}/bookmarked`)
    const htmlRespString = htmlResp.data
    // change display to reflect response data
    $('#music-content').empty().append(htmlRespString)
    // change active-tab 
    $target.parent().prev().removeClass('active-tab')
    $target.parent().addClass('active-tab')
}
$('#my-songs-tab').on('click', displayBookmarkedSongs)


//axios request to view posts without reload
async function displayPosts(evt){
    let $target = $(evt.target)
    const userId = $target.data("userid")
    // send request
    const htmlResp = await axios.get(`${BASE_URL}users/${userId}/posts`)
    const htmlRespString = htmlResp.data
    // change display to reflect response data
    $('#music-content').empty().append(htmlRespString)
    // change active-tab 
    $target.parent().next().removeClass('active-tab')
    $target.parent().addClass('active-tab')
}
$('#my-posts-tab').on('click', displayPosts)


// axios request to bookmark/unbookmark songs
async function toggleBookmark(evt){
    let $target = $(evt.target)
    // console.log($target)
    const songId = $target.parent().parent().attr('id')
    const songTitle = $target.parent().prev().find('a').first().text()
    const resp = await axios.post(`${BASE_URL}bookmark/${songId}`)
    if (resp){
        if ($target.hasClass('bi-bookmark')){
            $target.removeClass('bi-bookmark')
            $target.addClass('bi-bookmark-fill')
            displayToastMessage('Bookmarked', songTitle)
        }
        else{
            $target.removeClass('bi-bookmark-fill')
            $target.addClass('bi-bookmark')
            displayToastMessage('Unbookmarked', songTitle)
        }
    }
}
$('#music-content').on('click','.bookmark', toggleBookmark)


// Display toast and dynamic messaging
function displayToastMessage(message, song){
    const $toast = $('#liveToast')
    const toastBootstrap = bootstrap.Toast.getOrCreateInstance($toast)
    $('.toast-body').html(`${message}: <strong>${song}</strong>`)
    console.log
    toastBootstrap.show()
}


// Axios request to delete a post
function deletePost(evt){
    let $target = $(evt.target)
    const postId = $target.closest('.post').attr('id')
    // send request
    $('#delete-post').on('click', async function () {
        const modal = bootstrap.Modal.getInstance($('.staticPostModal'));
        modal.hide();
        const resp = await axios.delete(`${BASE_URL}posts/${postId}/delete`)
        // if request went through display success message, else error message
        if (resp.data.message === "Deleted"){
            let $postEl = $target.closest(`#${postId}`)
            $postEl.remove()
        }
    })
}
$('.bi-trash-fill').on('click', deletePost)


// Change display on search filter select dropdown
function filter_results(){
    const val = $('#filter-music').val();
    if (val === 'users'){
        $('#music-content').hide()
        $('#users-content').show()
    }
    else{
        $('#music-content').show()
        $('#users-content').hide()
    }
}
$('#filter-music').change(filter_results)


// Click event to play/pause track audio snippet
function playPause(evt){
    let $iconBtn = $(evt.target)
    // Grab audioId to select correct audio player object
    let audioId = $iconBtn.parent().prev().attr('id')
    let $audio = $(`#${audioId}`).get(0)
    // Change button icon displays and play/pause audio
    if ($iconBtn.hasClass('bi-play-fill')){
        $iconBtn.removeClass('bi-play-fill')
        $iconBtn.addClass('bi-pause-fill')
        $audio.play();
    }
    else{
        $iconBtn.removeClass('bi-pause-fill')
        $iconBtn.addClass('bi-play-fill')
        $audio.pause()
    }
}
$('#music-content').on('click','.play-pause', playPause)