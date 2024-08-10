function copyLink() {
    const copyButton = document.getElementById('copy-link-button');
    const originalText = copyButton.innerHTML;

    navigator.clipboard.writeText(invite_link).then(() => {
        copyButton.innerHTML = 'Link copied';
        setTimeout(() => {
            copyButton.innerHTML = originalText;
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy link: ', err);
    });
}

function confirmExit() {
    Swal.fire({
        title: 'Leave match?',
        text: "Are you sure you want to leave match?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Leave',
        cancelButtonText: 'Cancel'
    }).then((result) => {
        if (result.isConfirmed) {
            LeaveGame(game_code);
            // window.location.href = exit_link;
        }
    });
}